from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

STATUS_RULE = "status IN ('New','In Progress','Resolved')"
PRIORITY_RULE = "IN ('Low','Medium','High')"
CATEGORY_RULE = "IN ('Hardware','Software','Network','Access','Other')"


class Requester(Base):
    __tablename__ = "requesters"
    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    department: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint(STATUS_RULE, name="ck_tickets_status"),
        CheckConstraint("priority " + PRIORITY_RULE, name="ck_tickets_priority"),
        CheckConstraint("category " + CATEGORY_RULE, name="ck_tickets_category"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("requesters.id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(20), server_default="Other")
    priority: Mapped[str] = mapped_column(String(10), server_default="Medium")
    status: Mapped[str] = mapped_column(String(20), server_default="New")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class TicketActivity(Base):
    __tablename__ = "ticket_activity"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    action: Mapped[str] = mapped_column(String(30))
    note: Mapped[str | None] = mapped_column(Text)
    old_status: Mapped[str | None] = mapped_column(String(20))
    new_status: Mapped[str | None] = mapped_column(String(20))
    actor: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AISuggestion(Base):
    __tablename__ = "ai_suggestions"
    __table_args__ = (
        CheckConstraint("suggested_priority " + PRIORITY_RULE, name="ck_ai_priority"),
        CheckConstraint("suggested_category " + CATEGORY_RULE, name="ck_ai_category"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    suggested_category: Mapped[str] = mapped_column(String(20))
    suggested_priority: Mapped[str] = mapped_column(String(10))
    priority_reason: Mapped[str] = mapped_column(Text)
    troubleshooting_steps: Mapped[str] = mapped_column(Text)
    model_name: Mapped[str | None] = mapped_column(String(50))
    # True when instruction-like text was removed from the ticket before analysis
    input_flagged: Mapped[bool] = mapped_column(Boolean, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AIFeedback(Base):
    __tablename__ = "ai_feedback"
    __table_args__ = (
        CheckConstraint("final_priority " + PRIORITY_RULE, name="ck_feedback_priority"),
        CheckConstraint("final_category " + CATEGORY_RULE, name="ck_feedback_category"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    suggestion_id: Mapped[int] = mapped_column(ForeignKey("ai_suggestions.id"))
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    accepted: Mapped[bool] = mapped_column(Boolean)
    useful: Mapped[bool] = mapped_column(Boolean)
    final_category: Mapped[str] = mapped_column(String(20))
    final_priority: Mapped[str] = mapped_column(String(10))
    actor: Mapped[str | None] = mapped_column(String(100))
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())