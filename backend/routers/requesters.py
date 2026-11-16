from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from db import get_db
from models import Requester
from schemas import RequesterOut

router = APIRouter(prefix="/requesters", tags=["Requesters"])


@router.get("", response_model=list[RequesterOut])
def list_requesters(db: Session = Depends(get_db)):
    return db.scalars(select(Requester).order_by(Requester.display_name)).all()