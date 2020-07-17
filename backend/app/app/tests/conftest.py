from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User
from app.models.network import Network
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import get_superuser_token_headers, get_superuser


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> Dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest.fixture(scope="module")
def superuser(client: TestClient) -> User:
    return get_superuser(client)


@pytest.fixture(scope="module")
def normal_user(client: TestClient) -> User:
    db = SessionLocal()
    return create_random_user(db)


def clear_db():
    db = SessionLocal()
    try:
        num_rows_deleted = db.query(Network).delete()
        db.commit()
    except:
        db.rollback()


def pytest_sessionstart(session):
    clear_db()


def pytest_sessionfinish(session, exitstatus):
    clear_db()
