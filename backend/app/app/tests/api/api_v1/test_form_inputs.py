from datetime import date, timedelta
from fastapi.testclient import TestClient
from random import randint
from sqlalchemy.orm import Session

from app import crud
from app.schemas import PermissionTypeEnum
from app.core.config import settings
from app.tests.utils.form_input import create_random_form_input
from app.tests.utils.interface import create_random_interface
from app.tests.utils.node import create_random_node
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import random_lower_string
from app.tests.utils.setup import interface_permission_setup

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
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-inputs/",
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
        "an_integer": randint(0, 10000),
    }
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/{-1}/form-inputs/",
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
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-inputs/",
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
    setup = interface_permission_setup(db, permission_type=PermissionTypeEnum.create)
    user = setup["user"]
    interface = setup["interface"]
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
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.post(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-inputs/",
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
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-inputs/",
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
# region | Tests for Form Input read one endpoint --------------------------------------
# --------------------------------------------------------------------------------------


def test_read_form_input(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful form input read one"""
    interface = crud.interface.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    form_input = create_random_form_input(db)
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-inputs/{form_input.id}",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["id"] == form_input.id
    assert content["name"] == form_input.name
    assert content["date_created"] == str(form_input.date_created)
    assert content["an_integer"] == form_input.an_integer
    assert content["node_id"] == form_input.node_id


def test_read_form_input_fail_interface_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the indicated interface doesn't exist"""
    form_input = create_random_form_input(db)
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/{-1}/form-inputs/{form_input.id}",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_read_form_input_fail_interface_table_not_created(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the interface backing table hasn't been created"""
    interface = create_random_interface(db, table_name="fail_table_not_created2")
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-inputs/{1}",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        "The backing table for this interface has not been created."
    )


def test_read_form_input_fail_form_input_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the indicated form_input doesn't exist"""
    interface = crud.interface.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-inputs/{-1}",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find form input."


def test_read_form_input_normal_user(client: TestClient, db: Session) -> None:
    """Successful form input read one normal user"""
    setup = interface_permission_setup(db, permission_type=PermissionTypeEnum.read)
    interface = setup["interface"]
    user = setup["user"]
    form_input = create_random_form_input(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-inputs/{form_input.id}",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["id"] == form_input.id
    assert content["name"] == form_input.name
    assert content["date_created"] == str(form_input.date_created)
    assert content["an_integer"] == form_input.an_integer
    assert content["node_id"] == form_input.node_id


def test_read_form_input_normal_user_fail_no_permission(
    client: TestClient, db: Session
) -> None:
    """Fail if the normal user doesn't have permissions"""
    interface = crud.interface.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    user = create_random_user(db)
    form_input = create_random_form_input(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-inputs/{form_input.id}",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        f"User ID {user.id} does not have read permissions for "
        f"interface ID {interface.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Form Input read multi endpoint ------------------------------------
# --------------------------------------------------------------------------------------


def test_read_form_inputs(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful form input read multi"""
    interface = crud.interface.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    form_inputs = [create_random_form_input(db) for i in range(10)]
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-inputs/",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    stored_ids = [c["id"] for c in content]
    for form_input in form_inputs:
        assert form_input.id in stored_ids


def test_read_form_inputs_fail_interface_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the indicated interface doesn't exist"""
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/{-1}/form-inputs/",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_read_form_inputs_fail_table_not_created(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the interface backing table hasn't been created"""
    interface = create_random_interface(db, table_name="fail_table_not_created3")
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-inputs/",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        "The backing table for this interface has not been created."
    )


def test_read_form_inputs_normal_user(client: TestClient, db: Session) -> None:
    """Successful form input read multi normal user"""
    setup = interface_permission_setup(db, permission_type=PermissionTypeEnum.read)
    interface = setup["interface"]
    user = setup["user"]
    form_inputs = [create_random_form_input(db) for i in range(10)]
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-inputs/",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    stored_ids = [c["id"] for c in content]
    for form_input in form_inputs:
        assert form_input.id in stored_ids


def test_read_form_inputs_normal_user_fail_no_permission(
    client: TestClient, db: Session
) -> None:
    """Fail if the user doesn't have read permission on the interface"""
    interface = crud.interface.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    user = create_random_user(db)
    [create_random_form_input(db) for i in range(10)]
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/form-inputs/",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        f"User ID {user.id} does not have read permissions for "
        f"interface ID {interface.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Form Input update endpoint ----------------------------------------
# --------------------------------------------------------------------------------------
