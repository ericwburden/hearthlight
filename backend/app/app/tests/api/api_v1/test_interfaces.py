from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.tests.utils.interface import test_table_template, create_random_interface
from app.tests.utils.utils import random_lower_string

# --------------------------------------------------------------------------------------
# region | Tests for Interface create endpoint -----------------------------------------
# --------------------------------------------------------------------------------------


def test_create_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful interface creation"""
    data = {
        "name": random_lower_string(),
        "interface_type": "test",
        "table_template": test_table_template(),
    }
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["name"] == data["name"]
    assert content["interface_type"] == data["interface_type"]
    assert content["table_template"] == data["table_template"]


def test_create_interface_fail_duplicate_table_name(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """
    Interface creation should fail if the template table_name already
    exists
    """
    name = random_lower_string()
    interface_type = "test"
    table_template = test_table_template()
    interface_in = schemas.InterfaceCreate(
        name=name, interface_type=interface_type, table_template=table_template
    )
    crud.interface.create(db=db, obj_in=interface_in, created_by_id=1)
    data = {
        "name": name,
        "interface_type": interface_type,
        "table_template": table_template,
    }
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == (
        "An interface with that table name already exists, rename your template table."
    )


def test_create_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """If the user attempting to access the endpoint is not a superuser"""
    data = {
        "name": random_lower_string(),
        "interface_type": "test",
        "table_template": test_table_template(),
    }
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/",
        headers=normal_user_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Interface read one endpoint ---------------------------------------
# --------------------------------------------------------------------------------------


def test_read_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully retrieve an interface by ID"""
    interface = create_random_interface(db)
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/{interface.id}",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["id"] == interface.id
    assert content["name"] == interface.name
    assert content["interface_type"] == interface.interface_type
    assert content["table_template"] == interface.table_template


def test_read_interface_fail_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail when the interface doesn't exist"""
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/{-1}", headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_read_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """If the user attempting to access the endpoint is not a superuser"""
    interface = create_random_interface(db)
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/{interface.id}",
        headers=normal_user_token_headers,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Interface read multi endpoint -------------------------------------
# --------------------------------------------------------------------------------------


def test_read_multi_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully retrieve multiple interfaces"""
    interfaces = [create_random_interface(db) for i in range(10)]
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/", headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    for interface in interfaces:
        found_match = False
        for stored_interface in content:
            id_match = stored_interface["id"] == interface.id
            name_match = stored_interface["name"] == interface.name
            type_match = stored_interface["interface_type"] == interface.interface_type
            template_match = (
                stored_interface["table_template"] == interface.table_template
            )
            if id_match and name_match and type_match and template_match:
                found_match = True
                break
        assert found_match


def test_read_multi_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """Fail if the user is not a superuser"""
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/", headers=normal_user_token_headers,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Interface update endpoint -----------------------------------------
# --------------------------------------------------------------------------------------


def test_update_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully update an interface"""
    interface = create_random_interface(db)
    data = {"name": random_lower_string()}
    response = client.put(
        f"{settings.API_V1_STR}/interfaces/{interface.id}",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["name"] == data["name"]
    assert content["id"] == interface.id
    assert content["interface_type"] == interface.interface_type
    assert content["table_template"] == interface.table_template


def test_update_interface_fail_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the interface doesn't exist"""
    data = {"name": random_lower_string()}
    response = client.put(
        f"{settings.API_V1_STR}/interfaces/{-1}",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_update_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """Fail if the user is not a superuser"""
    interface = create_random_interface(db)
    data = {"name": random_lower_string()}
    response = client.put(
        f"{settings.API_V1_STR}/interfaces/{interface.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


def test_update_interface_fail_table_created(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    interface = create_random_interface(db)
    crud.interface.create_template_table(db, id=interface.id)
    data = {"table_template": test_table_template()}
    response = client.put(
        f"{settings.API_V1_STR}/interfaces/{interface.id}",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == (
        "Cannot modify the table template, the table has already been created."
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Interface delete endpoint -----------------------------------------
# --------------------------------------------------------------------------------------


def test_delete_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully delete an interface"""
    interface = create_random_interface(db)
    response = client.delete(
        f"{settings.API_V1_STR}/interfaces/{interface.id}",
        headers=superuser_token_headers,
    )
    stored_interface = crud.interface.get(db, id=interface.id)
    content = response.json()
    # breakpoint()
    assert response.status_code == 200
    assert content["name"] == interface.name
    assert stored_interface is None


def test_delete_interface_fail_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the interface doesn't exist"""
    response = client.delete(
        f"{settings.API_V1_STR}/interfaces/{-1}", headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_delete_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """Fail if the user is not a superuser"""
    interface = create_random_interface(db)
    response = client.delete(
        f"{settings.API_V1_STR}/interfaces/{interface.id}",
        headers=normal_user_token_headers,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Interface build table endpoint ------------------------------------
# --------------------------------------------------------------------------------------


def test_build_table_endpoint(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully build an interface's backing table"""
    interface = create_random_interface(db)
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/build_table",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["name"] == interface.name
    assert content["table_created"]


def test_build_table_fail_interface_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the interface doesn't exist"""
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/{-1}/build_table",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_build_table_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """Fail if the user is not a superuser"""
    interface = create_random_interface(db)
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/{interface.id}/build_table",
        headers=normal_user_token_headers,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
