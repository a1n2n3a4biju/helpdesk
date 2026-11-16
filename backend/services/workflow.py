from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Ticket, TicketActivity

ALLOWED_MOVES = {
    "New": {"In Progress"},
    "In Progress": {"Resolved"},
    "Resolved": {"In Progress"},
}


def change_status(db: Session, ticket: Ticket, new_status: str,
                  actor: str | None = None, note: str | None = None) -> None:
    allowed = ALLOWED_MOVES[ticket.status]
    if new_status not in allowed:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot change status from {ticket.status} to {new_status}. "
                   f"Allowed next status: {', '.join(sorted(allowed))}",
        )
    db.add(TicketActivity(ticket_id=ticket.id, action="status_change", note=note,
                          old_status=ticket.status, new_status=new_status, actor=actor))
    ticket.status = new_status


def change_priority(db: Session, ticket: Ticket, new_priority: str,
                    actor: str | None = None, note: str | None = None) -> None:
    if new_priority == ticket.priority:
        return
    text = f"Priority {ticket.priority} -> {new_priority}"
    db.add(TicketActivity(ticket_id=ticket.id, action="priority_change",
                          note=f"{text}: {note}" if note else text, actor=actor))
    ticket.priority = new_priority


def change_category(db: Session, ticket: Ticket, new_category: str,
                    actor: str | None = None, note: str | None = None) -> None:
    if new_category == ticket.category:
        return
    text = f"Category {ticket.category} -> {new_category}"
    db.add(TicketActivity(ticket_id=ticket.id, action="category_change",
                          note=f"{text}: {note}" if note else text, actor=actor))
    ticket.category = new_category


def add_comment(db: Session, ticket: Ticket, note: str,
                actor: str | None = None) -> TicketActivity:
    activity = TicketActivity(ticket_id=ticket.id, action="comment", note=note, actor=actor)
    db.add(activity)
    return activity