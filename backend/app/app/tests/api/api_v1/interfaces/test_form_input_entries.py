from datetime import date, timedelta
from fastapi.testclient import TestClient
from random import randint
from sqlalchemy.orm import Session

from app import crud
from app.schemas import PermissionTypeEnum
from app.core.config import settings
from app.tests.utils.form_input import (
    create_random_form_input_interface,
    create_random_form_input_table_entry,
)
from app.tests.utils.node import create_random_node
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import random_lower_string
from app.tests.utils.setup import form_input_permission_setup

# --------------------------------------------------------------------------------------
# region | Tests for Form Input entry create endpoint ----------------------------------
# --------------------------------------------------------------------------------------


def test_create_form_input_entry(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful form input entry creation"""
    node = create_random_node(db)
    data = {
        "name": random_lower_string(),
        "date_created": str(date(1985, 1, 1) + timedelta(days=randint(0, 9999))),
        "an_integer": randint(0, 10000),
        "node_id": node.id,
    }
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}/entries/",
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


def test_create_form_input_entry_fail_interface_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the specified interface doesn't exist"""
    data = {
        "name": random_lower_string(),
        "date_created": str(date(1985, 1, 1) + timedelta(days=randint(0, 9999))),
        "an_integer": randint(0, 10000),
    }
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{-1}/entries/",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_create_form_input_entry_fail_interface_table_not_created(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the interface backing table hasn't been created"""
    form_input = create_random_form_input_interface(
        db, table_name="fail_table_not_created"
    )
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}/entries/",
        headers=superuser_token_headers,
        json={},
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        "The backing table for this interface has not been created."
    )


def test_create_form_input_entry_normal_user(client: TestClient, db: Session) -> None:
    """Successful form input entry creation by normal user"""
    setup = form_input_permission_setup(db, permission_type=PermissionTypeEnum.create)
    user = setup["user"]
    form_input = setup["form_input"]
    node = create_random_node(db)
    data = {
        "name": random_lower_string(),
        "date_created": str(date(1985, 1, 1) + timedelta(days=randint(0, 9999))),
        "an_integer": randint(0, 10000),
        "node_id": node.id,
    }
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.post(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}/entries/",
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


def test_create_form_input_entry_normal_user_fail_no_permission(
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
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    user = create_random_user(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.post(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}/entries/",
        headers=user_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        f"User ID {user.id} does not have "
        f"create permissions for "
        f"interface ID {form_input.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Form Input entry read one endpoint --------------------------------
# --------------------------------------------------------------------------------------


def test_read_form_input_entry(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful form input entry read one"""
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    form_input_entry = create_random_form_input_table_entry(db)
    response = client.get(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{form_input.id}/entries/{form_input_entry.id}"
        ),
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["id"] == form_input_entry.id
    assert content["name"] == form_input_entry.name
    assert content["date_created"] == str(form_input_entry.date_created)
    assert content["an_integer"] == form_input_entry.an_integer
    assert content["node_id"] == form_input_entry.node_id
    assert content["interface_id"] == form_input.id


def test_read_form_input_entry_fail_interface_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the indicated interface doesn't exist"""
    form_input_entry = create_random_form_input_table_entry(db)
    response = client.get(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{-1}/entries/{form_input_entry.id}"
        ),
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_read_form_input_entry_fail_interface_table_not_created(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the interface backing table hasn't been created"""
    form_input = create_random_form_input_interface(
        db, table_name="fail_table_not_created2"
    )
    response = client.get(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{form_input.id}/entries/{-1}"
        ),
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        "The backing table for this interface has not been created."
    )


def test_read_form_input_entry_fail_form_input_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the indicated form input entry doesn't exist"""
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    response = client.get(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{form_input.id}/entries/{-1}"
        ),
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find form input entry."


def test_read_form_input_entry_normal_user(client: TestClient, db: Session) -> None:
    """Successful form input entry read one normal user"""
    setup = form_input_permission_setup(db, permission_type=PermissionTypeEnum.read)
    form_input = setup["form_input"]
    user = setup["user"]
    form_input_entry = create_random_form_input_table_entry(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.get(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{form_input.id}/entries/{form_input_entry.id}"
        ),
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["id"] == form_input_entry.id
    assert content["name"] == form_input_entry.name
    assert content["date_created"] == str(form_input_entry.date_created)
    assert content["an_integer"] == form_input_entry.an_integer
    assert content["node_id"] == form_input_entry.node_id
    assert content["interface_id"] == form_input.id


def test_read_form_input_entry_normal_user_fail_no_permission(
    client: TestClient, db: Session
) -> None:
    """Fail if the normal user doesn't have permissions"""
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    user = create_random_user(db)
    form_input_entry = create_random_form_input_table_entry(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.get(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{form_input.id}/entries/{form_input_entry.id}"
        ),
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        f"User ID {user.id} does not have read permissions for "
        f"interface ID {form_input.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Form Input entry read multi endpoint ------------------------------
# --------------------------------------------------------------------------------------


def test_read_form_input_entries(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful form input entry read multi"""
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    form_input_entries = [create_random_form_input_table_entry(db) for i in range(10)]
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}/entries/",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    stored_ids = [c["id"] for c in content["records"]]
    for form_input_entry in form_input_entries:
        assert form_input_entry.id in stored_ids


def test_read_form_input_entries_fail_interface_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the indicated interface doesn't exist"""
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{-1}/entries/",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_read_form_input_entries_fail_table_not_created(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the interface backing table hasn't been created"""
    form_input = create_random_form_input_interface(
        db, table_name="fail_table_not_created3"
    )
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}/entries/",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        "The backing table for this interface has not been created."
    )


def test_read_form_input_entries_normal_user(client: TestClient, db: Session) -> None:
    """Successful form input read multi normal user"""
    setup = form_input_permission_setup(db, permission_type=PermissionTypeEnum.read)
    form_input = setup["form_input"]
    user = setup["user"]
    form_input_entries = [create_random_form_input_table_entry(db) for i in range(10)]
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}/entries/",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    stored_ids = [c["id"] for c in content["records"]]
    for form_input_entry in form_input_entries:
        assert form_input_entry.id in stored_ids


def test_read_form_input_entries_normal_user_fail_no_permission(
    client: TestClient, db: Session
) -> None:
    """Fail if the user doesn't have read permission on the interface"""
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    user = create_random_user(db)
    [create_random_form_input_table_entry(db) for i in range(10)]
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}/entries/",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        f"User ID {user.id} does not have read permissions for "
        f"interface ID {form_input.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Form Input entry update endpoint ----------------------------------
# --------------------------------------------------------------------------------------


def test_update_form_input_entry(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful form input entry update"""
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    form_input_entry = create_random_form_input_table_entry(db)
    data = {"name": random_lower_string()}
    response = client.put(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{form_input.id}/entries/{form_input_entry.id}"
        ),
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["id"] == form_input_entry.id
    assert content["name"] == data["name"]
    assert content["date_created"] == str(form_input_entry.date_created)
    assert content["an_integer"] == form_input_entry.an_integer
    assert content["node_id"] == form_input_entry.node_id


def test_update_form_input_entry_fail_interface_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the specified interface doesn't exist"""
    form_input_entry = create_random_form_input_table_entry(db)
    data = {"name": random_lower_string()}
    response = client.put(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{-1}/entries/{form_input_entry.id}"
        ),
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_update_form_input_entry_fail_form_input_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the specified form input record doesn't exist"""
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    data = {"name": random_lower_string()}
    response = client.put(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{form_input.id}/entries/{-1}"
        ),
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find form input record."


def test_update_form_input_entry_fail_interface_table_not_created(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the specified interface doesn't have a backing table"""
    form_input = create_random_form_input_interface(
        db, table_name="fail_table_not_created4"
    )
    form_input_entry = create_random_form_input_table_entry(db)
    data = {"name": random_lower_string()}
    response = client.put(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{form_input.id}/entries/{form_input_entry.id}"
        ),
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        "The backing table for this interface has not been created."
    )


def test_update_form_input_entry_normal_user(client: TestClient, db: Session) -> None:
    """Successful form input update by a normal user"""
    setup = form_input_permission_setup(db, permission_type=PermissionTypeEnum.update)
    form_input = setup["form_input"]
    user = setup["user"]
    form_input_entry = create_random_form_input_table_entry(db)
    data = {"name": random_lower_string()}
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.put(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{form_input.id}/entries/{form_input_entry.id}"
        ),
        headers=user_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["id"] == form_input_entry.id
    assert content["name"] == data["name"]
    assert content["date_created"] == str(form_input_entry.date_created)
    assert content["an_integer"] == form_input_entry.an_integer
    assert content["node_id"] == form_input_entry.node_id


def test_update_form_input_entry_normal_user_fail_no_permission(
    client: TestClient, db: Session
) -> None:
    """Fail if the normal user doesn't have update permissions"""
    setup = form_input_permission_setup(
        db, permission_type=PermissionTypeEnum.update, permission_enabled=False
    )
    form_input = setup["form_input"]
    user = setup["user"]
    form_input_entry = create_random_form_input_table_entry(db)
    data = {"name": random_lower_string()}
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.put(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{form_input.id}/entries/{form_input_entry.id}"
        ),
        headers=user_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        f"User ID {user.id} does not have update permissions for "
        f"interface ID {form_input.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Form Input delete endpoint ----------------------------------------
# --------------------------------------------------------------------------------------


def test_delete_form_input_entry(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful form input deletion"""
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    form_input_entry = create_random_form_input_table_entry(db)
    response = client.delete(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{form_input.id}/entries/{form_input_entry.id}"
        ),
        headers=superuser_token_headers,
    )
    form_input_crud = crud.form_input.get_table_crud(db, id=form_input.id)
    stored_form_input_entry = form_input_crud.get(db, id=form_input_entry.id)
    content = response.json()
    assert response.status_code == 200
    assert content["id"] == form_input_entry.id
    assert content["name"] == form_input_entry.name
    assert content["date_created"] == str(form_input_entry.date_created)
    assert content["an_integer"] == form_input_entry.an_integer
    assert content["node_id"] == form_input_entry.node_id
    assert stored_form_input_entry is None


def test_delete_form_input_entry_fail_interface_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the specified interface doesn't exist"""
    form_input_entry = create_random_form_input_table_entry(db)
    response = client.delete(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{-1}/entries/{form_input_entry.id}"
        ),
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_delete_form_input_entry_fail_form_input_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the specified form input record doesn't exist"""
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    response = client.delete(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}/entries/{-1}",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find form input entry."


def test_delete_form_input_entry_fail_interface_table_not_created(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the specified interface doesn't have a backing table"""
    form_input = create_random_form_input_interface(
        db, table_name="fail_table_not_created5"
    )
    form_input_entry = create_random_form_input_table_entry(db)
    response = client.delete(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{form_input.id}/entries/{form_input_entry.id}"
        ),
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        "The backing table for this interface has not been created."
    )


def test_delete_form_input_entry_normal_user(client: TestClient, db: Session) -> None:
    """Successful form input delete by a normal user"""
    setup = form_input_permission_setup(db, permission_type=PermissionTypeEnum.delete)
    form_input = setup["form_input"]
    user = setup["user"]
    form_input_entry = create_random_form_input_table_entry(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.delete(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{form_input.id}/entries/{form_input_entry.id}"
        ),
        headers=user_token_headers,
    )
    form_input_crud = crud.form_input.get_table_crud(db, id=form_input.id)
    stored_form_input_entry = form_input_crud.get(db, id=form_input_entry.id)
    content = response.json()
    assert response.status_code == 200
    assert content["id"] == form_input_entry.id
    assert content["name"] == form_input_entry.name
    assert content["date_created"] == str(form_input_entry.date_created)
    assert content["an_integer"] == form_input_entry.an_integer
    assert content["node_id"] == form_input_entry.node_id
    assert stored_form_input_entry is None


def test_delete_form_input_entry_normal_user_fail_no_permission(
    client: TestClient, db: Session
) -> None:
    """Fail if the normal user doesn't have delete permissions"""
    setup = form_input_permission_setup(
        db, permission_type=PermissionTypeEnum.delete, permission_enabled=False
    )
    form_input = setup["form_input"]
    user = setup["user"]
    form_input_entry = create_random_form_input_interface(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.delete(
        (
            f"{settings.API_V1_STR}/interfaces/form-inputs/"
            f"{form_input.id}/entries/{form_input_entry.id}"
        ),
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        f"User ID {user.id} does not have delete permissions for "
        f"interface ID {form_input.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
