from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import MetaData

from app import crud
from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.main import app

from app.models.node import Node
from app.models.user import User
from app.models.user_group import UserGroup, UserGroupUserRel, UserGroupPermissionRel
from app.models.permission import Permission, NodePermission
from app.models.interface import Interface

from app.schemas.interface import InterfaceCreate
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

    models = [
        UserGroupPermissionRel,
        NodePermission,
        Permission,
        UserGroupUserRel,
        UserGroup,
        Node,
        Interface,
        User,
    ]
    model_table_names = [m.__tablename__ for m in models]
    model_table_names.append("alembic_version")
    # Drop records from the static tables
    for model in models:
        try:
            if model.__tablename__ == "user":  # leave the superuser
                db.query(model).filter(model.id > 1).delete()
            else:
                db.query(model).delete()
            # print(f'Deleted {n} {model.__name__}s')
            db.commit()
        except Exception as e:
            print(f"Failed to delete {model}s")
            print(e)
            db.rollback()

    # Drop the dynamically created interface tables
    metadata = MetaData()
    metadata.bind = engine
    metadata.reflect(bind=engine)
    all_tables = metadata.tables
    for name, table in all_tables.items():
        if name not in model_table_names:
            table.drop()


def create_interface_form_input_testing_table():
    db = SessionLocal()
    name = "form_input_test_table"
    interface_type = "test"
    table_template = {
        "table_name": name,
        "columns": [
            {
                "column_name": "id",
                "data_type": "Integer",
                "kwargs": {"primary_key": True, "index": True},
            },
            {
                "column_name": "name",
                "data_type": "String(256)",
                "kwargs": {"unique": True, "nullable": False},
            },
            {
                "column_name": "date_created",
                "data_type": "Date",
                "kwargs": {"nullable": False},
            },
            {"column_name": "an_integer", "data_type": "Integer"},
            {
                "column_name": "node_id",
                "data_type": "Integer",
                "args": ["ForeignKey('node.id')"],
                "kwargs": {"nullable": True},
            },
        ],
    }
    interface_in = InterfaceCreate(
        name=name, interface_type=interface_type, table_template=table_template
    )
    interface = crud.interface.create(db=db, obj_in=interface_in, created_by_id=1)
    crud.interface.create_template_table(db, id=interface.id)


def pytest_sessionstart(session):
    clear_db()
    create_interface_form_input_testing_table()


def pytest_sessionfinish(session, exitstatus):
    # clear_db()
    pass
