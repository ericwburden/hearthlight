import random
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.schemas import PermissionTypeEnum
from app.tests.utils.form_input import create_random_form_input_interface
from app.tests.utils.query import create_random_query_interface


def create_random_interface(db):
    die = random.randint(0, 100)
    if die < 50:
        return create_random_form_input_interface(db)
    return create_random_query_interface(db)


def test_read_interfaces(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully read multiple entered interfaces"""

    interfaces = [create_random_interface(db) for i in range(10)]
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/",
        headers=superuser_token_headers,
    )
    content = response.json()
    stored_node_ids = [node["id"] for node in content["records"]]
    assert response.status_code == 200
    assert len(content["records"]) >= 10
    assert all([n.id in stored_node_ids for n in interfaces])


def test_read_multi_form_input_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """Fail if the user is not a superuser"""
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/",
        headers=normal_user_token_headers,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"