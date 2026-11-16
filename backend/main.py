from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from db import get_db

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Helpdesk backend is running"}

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    version = db.execute(text("SELECT version()")).scalar()
    return {"database": "connected", "version": version}