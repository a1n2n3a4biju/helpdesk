from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from config import settings
from db import get_db
from routers import dashboard, requesters, tickets

app = FastAPI(title="AI Employee Helpdesk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(requesters.router)
app.include_router(tickets.router)
app.include_router(dashboard.router)


@app.get("/")
def home():
    return {"message": "Helpdesk backend is running"}


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    version = db.execute(text("SELECT version()")).scalar()
    return {"database": "connected", "version": version}