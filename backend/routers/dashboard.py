from typing import get_args
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from db import get_db
from models import Ticket
from schemas import DashboardSummary, Priority, Status

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def count_by(db: Session, column, all_values) -> dict[str, int]:
    counts = {value: 0 for value in all_values}
    rows = db.execute(select(column, func.count()).group_by(column)).all()
    for value, number in rows:
        counts[value] = number
    return counts


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    by_status = count_by(db, Ticket.status, get_args(Status))
    by_priority = count_by(db, Ticket.priority, get_args(Priority))
    return {"total": sum(by_status.values()),
            "by_status": by_status,
            "by_priority": by_priority}