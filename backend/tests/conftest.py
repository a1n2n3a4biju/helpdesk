import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import settings
from db import get_db
from main import app
from models import Requester

if not settings.test_database_url or "helpdesk_test" not in settings.test_database_url:
    raise RuntimeError("TEST_DATABASE_URL must be set and point to the helpdesk_test database")

test_engine = create_engine(settings.test_database_url)


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def requester(db_session):
    person = Requester(display_name="Test User", email="test.user@example.com", department="QA")
    db_session.add(person)
    db_session.flush()
    return person