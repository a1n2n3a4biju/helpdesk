from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Status = Literal["New", "In Progress", "Resolved"]
Priority = Literal["Low", "Medium", "High"]
Category = Literal["Hardware", "Software", "Network", "Access", "Other"]


class RequesterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    display_name: str
    email: str
    department: str | None


class TicketCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    requester_id: int
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=10)
    category: Category | None = None


class TicketUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str | None = Field(default=None, min_length=5, max_length=200)
    description: str | None = Field(default=None, min_length=10)
    category: Category | None = None


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    requester_id: int
    title: str
    description: str
    category: Category
    priority: Priority
    status: Status
    created_at: datetime
    updated_at: datetime


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ticket_id: int
    action: str
    note: str | None
    old_status: str | None
    new_status: str | None
    actor: str | None
    created_at: datetime

class StatusUpdate(BaseModel):
    status: Status
    actor: str | None = Field(default=None, max_length=100)
    note: str | None = None


class PriorityUpdate(BaseModel):
    priority: Priority
    actor: str | None = Field(default=None, max_length=100)
    note: str | None = None


class CommentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    note: str = Field(min_length=2, max_length=2000)
    actor: str | None = Field(default=None, max_length=100)

class DashboardSummary(BaseModel):
    total: int
    by_status: dict[str, int]
    by_priority: dict[str, int]

# ---------- AI suggestions and feedback ----------

class AIStatus(BaseModel):
    available: bool
    model: str
    model_installed: bool
    detail: str


class FeedbackCreate(BaseModel):
    """Staff decision on an AI suggestion. `accepted` is worked out by the server:
    true when the final values equal the AI's suggested values."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    suggestion_id: int
    useful: bool
    final_category: Category
    final_priority: Priority
    actor: str | None = Field(default=None, max_length=100)
    comment: str | None = Field(default=None, max_length=1000)


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    suggestion_id: int
    ticket_id: int
    accepted: bool
    useful: bool
    final_category: Category
    final_priority: Priority
    actor: str | None
    comment: str | None
    created_at: datetime


class SuggestionOut(BaseModel):
    """AI proposal, kept separate from the ticket's staff-confirmed category/priority."""
    id: int
    ticket_id: int
    suggested_category: Category
    suggested_priority: Priority
    priority_reason: str
    troubleshooting_steps: list[str]
    model_name: str | None
    input_flagged: bool
    created_at: datetime
    feedback: FeedbackOut | None = None
