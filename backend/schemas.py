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