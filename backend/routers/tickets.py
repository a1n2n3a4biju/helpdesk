from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from db import get_db
from models import Requester, Ticket, TicketActivity
from schemas import (ActivityOut, Category, CommentCreate, Priority, PriorityUpdate,
                     Status, StatusUpdate, TicketCreate, TicketOut, TicketUpdate)
import logging

from services import workflow

log = logging.getLogger("helpdesk.tickets")
router = APIRouter(prefix="/tickets", tags=["Tickets"])


def get_ticket_or_404(db: Session, ticket_id: int) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return ticket


@router.post("", response_model=TicketOut, status_code=201)
def create_ticket(data: TicketCreate, db: Session = Depends(get_db)):
    requester = db.get(Requester, data.requester_id)
    if requester is None:
        raise HTTPException(status_code=422, detail=[{
            "loc": ["body", "requester_id"],
            "msg": f"Requester {data.requester_id} does not exist",
            "type": "value_error",
        }])
    ticket = Ticket(
        requester_id=data.requester_id,
        title=data.title,
        description=data.description,
        category=data.category or "Other",
        priority="Medium",
        status="New",
    )
    db.add(ticket)
    db.flush()  # gives the new ticket its ID before we write history
    db.add(TicketActivity(ticket_id=ticket.id, action="created", note="Ticket raised",
                          new_status="New", actor=requester.display_name))
    db.commit()
    db.refresh(ticket)
    log.info("ticket.created ticket_id=%s requester_id=%s category=%s", ticket.id, ticket.requester_id, ticket.category)
    return ticket


@router.get("", response_model=list[TicketOut])
def list_tickets(status: Status | None = None, category: Category | None = None,
                 priority: Priority | None = None, requester_id: int | None = None,
                 db: Session = Depends(get_db)):
    query = select(Ticket).order_by(Ticket.created_at.desc())
    if status:
        query = query.where(Ticket.status == status)
    if category:
        query = query.where(Ticket.category == category)
    if priority:
        query = query.where(Ticket.priority == priority)
    if requester_id:
        query = query.where(Ticket.requester_id == requester_id)
    return db.scalars(query).all()


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    return get_ticket_or_404(db, ticket_id)


@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, data: TicketUpdate, db: Session = Depends(get_db)):
    ticket = get_ticket_or_404(db, ticket_id)
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    if changes:
        for field, value in changes.items():
            setattr(ticket, field, value)
        db.add(TicketActivity(ticket_id=ticket.id, action="updated",
                              note="Updated: " + ", ".join(changes)))
        db.commit()
        db.refresh(ticket)
        log.info("ticket.updated ticket_id=%s fields=%s", ticket.id, ",".join(changes))
    return ticket


@router.get("/{ticket_id}/history", response_model=list[ActivityOut])
def ticket_history(ticket_id: int, db: Session = Depends(get_db)):
    get_ticket_or_404(db, ticket_id)
    query = (select(TicketActivity)
             .where(TicketActivity.ticket_id == ticket_id)
             .order_by(TicketActivity.created_at, TicketActivity.id))
    return db.scalars(query).all()

@router.patch("/{ticket_id}/status", response_model=TicketOut,
              responses={404: {"description": "Ticket not found"},
                         409: {"description": "Status change not allowed"}})
def update_status(ticket_id: int, data: StatusUpdate, db: Session = Depends(get_db)):
    ticket = get_ticket_or_404(db, ticket_id)
    old_status = ticket.status
    try:
        workflow.change_status(db, ticket, data.status, data.actor, data.note)
    except HTTPException:
        log.warning("ticket.status_rejected ticket_id=%s from=%s to=%s", ticket.id, old_status, data.status)
        raise
    db.commit()
    log.info("ticket.status_changed ticket_id=%s from=%s to=%s", ticket.id, old_status, data.status)
    db.refresh(ticket)
    return ticket


@router.patch("/{ticket_id}/priority", response_model=TicketOut,
              responses={404: {"description": "Ticket not found"}})
def update_priority(ticket_id: int, data: PriorityUpdate, db: Session = Depends(get_db)):
    ticket = get_ticket_or_404(db, ticket_id)
    old_priority = ticket.priority
    workflow.change_priority(db, ticket, data.priority, data.actor, data.note)
    db.commit()
    log.info("ticket.priority_changed ticket_id=%s from=%s to=%s", ticket.id, old_priority, data.priority)
    db.refresh(ticket)
    return ticket


@router.post("/{ticket_id}/comments", response_model=ActivityOut, status_code=201,
             responses={404: {"description": "Ticket not found"}})
def create_comment(ticket_id: int, data: CommentCreate, db: Session = Depends(get_db)):
    ticket = get_ticket_or_404(db, ticket_id)
    activity = workflow.add_comment(db, ticket, data.note, data.actor)
    db.commit()
    db.refresh(activity)
    log.info("ticket.comment_added ticket_id=%s activity_id=%s", ticket.id, activity.id)
    return activity