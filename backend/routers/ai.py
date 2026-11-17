"""AI analysis and human feedback endpoints.

Human control rules enforced here:
- Analysis only stores a proposal in ai_suggestions. It never changes the ticket.
- Only the feedback endpoint (a staff action) updates the ticket's category/priority,
  and it never touches status. Nothing in the AI flow can resolve a ticket.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import settings
from db import get_db
from models import AIFeedback, AISuggestion, Ticket
from schemas import AIStatus, FeedbackCreate, FeedbackOut, SuggestionOut
from services import ai, workflow

router = APIRouter(tags=["AI"])
log = logging.getLogger("helpdesk.ai")

AI_ERRORS = {
    502: {"description": "Model returned invalid content; nothing was saved"},
    503: {"description": "Model not running, not installed or timed out; nothing was saved"},
}


def get_ticket_or_404(db: Session, ticket_id: int) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return ticket


def to_suggestion_out(suggestion: AISuggestion, feedback: AIFeedback | None = None) -> SuggestionOut:
    return SuggestionOut(
        id=suggestion.id,
        ticket_id=suggestion.ticket_id,
        suggested_category=suggestion.suggested_category,
        suggested_priority=suggestion.suggested_priority,
        priority_reason=suggestion.priority_reason,
        troubleshooting_steps=[s for s in suggestion.troubleshooting_steps.split("\n") if s],
        model_name=suggestion.model_name,
        input_flagged=suggestion.input_flagged,
        created_at=suggestion.created_at,
        feedback=FeedbackOut.model_validate(feedback) if feedback else None,
    )


@router.get("/ai/status", response_model=AIStatus)
def ai_status():
    """Is the local model reachable? The UI can use this to show an 'AI offline' badge."""
    return ai.model_status()


@router.post("/tickets/{ticket_id}/analyze", response_model=SuggestionOut, status_code=201,
             responses={404: {"description": "Ticket not found"}, **AI_ERRORS})
def analyze_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Ask the local model for an advisory category, priority and troubleshooting steps.
    The suggestion is stored separately; the ticket itself is not changed."""
    ticket = get_ticket_or_404(db, ticket_id)
    try:
        result, flagged = ai.analyze_ticket(ticket.id, ticket.title, ticket.description)
    except ai.AIUnavailableError as exc:
        raise HTTPException(status_code=503,
                            detail=f"AI analysis unavailable: {exc}. The ticket can still be managed manually.")
    except ai.AIInvalidOutputError:
        raise HTTPException(status_code=502,
                            detail="AI returned an invalid answer, so it was not saved. "
                                   "Try again or continue manually.")
    suggestion = AISuggestion(
        ticket_id=ticket.id,
        suggested_category=result.category,
        suggested_priority=result.priority,
        priority_reason=result.priority_reason,
        troubleshooting_steps="\n".join(result.troubleshooting_steps),
        model_name=settings.ollama_model,
        input_flagged=flagged,
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    log.info("ai.suggestion_saved ticket_id=%s suggestion_id=%s", ticket.id, suggestion.id)
    return to_suggestion_out(suggestion)


@router.get("/tickets/{ticket_id}/suggestions", response_model=list[SuggestionOut],
            responses={404: {"description": "Ticket not found"}})
def list_suggestions(ticket_id: int, db: Session = Depends(get_db)):
    """All AI suggestions for a ticket, newest first, each with its latest staff feedback."""
    get_ticket_or_404(db, ticket_id)
    suggestions = db.scalars(select(AISuggestion)
                             .where(AISuggestion.ticket_id == ticket_id)
                             .order_by(AISuggestion.created_at.desc(), AISuggestion.id.desc())).all()
    feedback_rows = db.scalars(select(AIFeedback)
                               .where(AIFeedback.ticket_id == ticket_id)
                               .order_by(AIFeedback.created_at, AIFeedback.id)).all()
    latest = {row.suggestion_id: row for row in feedback_rows}  # later rows overwrite earlier ones
    return [to_suggestion_out(s, latest.get(s.id)) for s in suggestions]


@router.post("/tickets/{ticket_id}/feedback", response_model=FeedbackOut, status_code=201,
             responses={404: {"description": "Ticket or suggestion not found"}})
def give_feedback(ticket_id: int, data: FeedbackCreate, db: Session = Depends(get_db)):
    """Staff accept or correct an AI suggestion and mark it useful or not.
    The final values become the ticket's confirmed category/priority (with history rows).
    Status is never changed here."""
    ticket = get_ticket_or_404(db, ticket_id)
    suggestion = db.get(AISuggestion, data.suggestion_id)
    if suggestion is None or suggestion.ticket_id != ticket.id:
        raise HTTPException(status_code=404,
                            detail=f"Suggestion {data.suggestion_id} not found for ticket {ticket_id}")

    accepted = (data.final_category == suggestion.suggested_category
                and data.final_priority == suggestion.suggested_priority)
    feedback = AIFeedback(
        suggestion_id=suggestion.id,
        ticket_id=ticket.id,
        accepted=accepted,
        useful=data.useful,
        final_category=data.final_category,
        final_priority=data.final_priority,
        actor=data.actor,
        comment=data.comment,
    )
    db.add(feedback)
    reason = "AI suggestion accepted" if accepted else "AI suggestion corrected by staff"
    workflow.change_category(db, ticket, data.final_category, data.actor, reason)
    workflow.change_priority(db, ticket, data.final_priority, data.actor, reason)
    db.commit()
    db.refresh(feedback)
    log.info("ai.feedback_recorded ticket_id=%s suggestion_id=%s accepted=%s useful=%s "
             "final_category=%s final_priority=%s",
             ticket.id, suggestion.id, accepted, data.useful, data.final_category, data.final_priority)
    return feedback
