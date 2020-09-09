from datetime import date, timedelta
from fastapi.testclient import TestClient
from random import randint
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.tests.utils.interface import create_random_interface
from app.tests.utils.node import create_random_node
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.user_group import create_random_user_group
from app.tests.utils.utils import random_lower_string

# --------------------------------------------------------------------------------------
# region | Tests for Form Input create endpoint ----------------------------------------
# --------------------------------------------------------------------------------------


def test_create_form_input(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful form input creation"""
    node = create_random_node(db)
    data = {
        "name": random_lower_string(),
        "date_created": str(date(1985, 1, 1) + timedelta(days=randint(0, 9999))),
        "an_integer": randint(0, 10000),
        "node_id": node.id,
    }
    interface = crud.interface.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-input",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["id"]
    assert content["name"] == data["name"]
    assert content["date_created"] == data["date_created"]
    assert content["an_integer"] == data["an_integer"]
    assert content["node_id"] == data["node_id"]


def test_create_form_input_fail_interface_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the specified interface doesn't exist"""
    data = {
        "name": random_lower_string(),
        "date_created": str(date(1985, 1, 1) + timedelta(days=randint(0, 9999))),
        "an_integer": randint(0, 10000)
    }
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/{-1}/form-input",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_create_form_input_fail_interface_table_not_created(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the interface backing table hasn't been created"""
    interface = create_random_interface(db, table_name="fail_table_not_created")
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-input",
        headers=superuser_token_headers,
        json={},
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        "The backing table for this interface has not been created."
    )


def test_create_form_input_normal_user(client: TestClient, db: Session) -> None:
    """Successful form input creation by normal user"""
    node = create_random_node(db)
    data = {
        "name": random_lower_string(),
        "date_created": str(date(1985, 1, 1) + timedelta(days=randint(0, 9999))),
        "an_integer": randint(0, 10000),
        "node_id": node.id,
    }
    interface = crud.interface.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    user = create_random_user(db)
    user_group = create_random_user_group(db)
    create_permission = crud.interface.get_permission(
        db, id=interface.id, permission_type=schemas.PermissionTypeEnum.create
    )
    crud.user_group.add_user(db, user_group=user_group, user_id=user.id)
    crud.permission.grant(
        db, user_group_id=user_group.id, permission_id=create_permission.id
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.post(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-input",
        headers=user_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["id"]
    assert content["name"] == data["name"]
    assert content["date_created"] == data["date_created"]
    assert content["an_integer"] == data["an_integer"]
    assert content["node_id"] == data["node_id"]


def test_create_form_input_normal_user_fail_no_permission(
    client: TestClient, db: Session
) -> None:
    """Fail if the normal user doesn't have create permissions"""
    node = create_random_node(db)
    data = {
        "name": random_lower_string(),
        "date_created": str(date(1985, 1, 1) + timedelta(days=randint(0, 9999))),
        "an_integer": randint(0, 10000),
        "node_id": node.id,
    }
    interface = crud.interface.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    user = create_random_user(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.post(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-input",
        headers=user_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        f"User ID {user.id} does not have "
        f"create permissions for "
        f"interface ID {interface.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
