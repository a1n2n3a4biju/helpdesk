from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from config import settings
from db import get_db
from logging_setup import log_requests, setup_logging
from routers import ai, dashboard, requesters, tickets

setup_logging(settings.log_level, settings.log_file)

app = FastAPI(
    title="AI Employee Helpdesk API",
    description="REST API for raising, tracking and resolving IT support tickets, "
                "with advisory AI suggestions. Staff keep final control of every ticket.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(log_requests)

app.include_router(requesters.router)
app.include_router(tickets.router)
app.include_router(dashboard.router)
app.include_router(ai.router)


@app.get("/")
def home():
    return {"message": "Helpdesk backend is running"}


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    version = db.execute(text("SELECT version()")).scalar()
    return {"database": "connected", "version": version}