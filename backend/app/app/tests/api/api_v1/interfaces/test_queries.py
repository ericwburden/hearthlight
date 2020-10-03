from fastapi.testclient import TestClient
from random import randint
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.schemas import PermissionTypeEnum
from app.tests.utils.interface import test_query_template
from app.tests.utils.setup import query_permission_setup
from app.tests.utils.query import create_random_query_interface
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import random_lower_string


QUERY_INTERFACE_TYPE = "query_interface"

# --------------------------------------------------------------------------------------
# region | Tests for Query Interface create endpoint -----------------------------------
# --------------------------------------------------------------------------------------


def test_create_form_input_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful query creation"""
    data = {
        "name": random_lower_string(),
        "template": test_query_template().dict(),
        "refresh_interval": randint(36000, 576000),
    }
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/queries/",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["name"] == data["name"]
    assert content["interface_type"] == QUERY_INTERFACE_TYPE
    assert content["template"] == data["template"]
    assert content["refresh_interval"] == data["refresh_interval"]


def test_create_form_input_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """If the user attempting to access the endpoint is not a superuser"""
    data = {
        "name": random_lower_string(),
        "template": test_query_template().dict(),
        "refresh_interval": randint(36000, 576000),
    }
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/queries/",
        headers=normal_user_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Query Interface read one endpoint ---------------------------------
# --------------------------------------------------------------------------------------


def test_read_form_input_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully retrieve a query by ID"""
    query = create_random_query_interface(db)
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/queries/{query.id}",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["id"] == query.id
    assert content["name"] == query.name
    assert content["interface_type"] == QUERY_INTERFACE_TYPE
    assert content["template"] == query.template
    assert content["refresh_interval"] == query.refresh_interval


def test_read_form_input_interface_fail_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail when the query interface doesn't exist"""
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/queries/{-1}",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find query."


def test_read_form_input_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """If the user attempting to access the endpoint is not a superuser"""
    form_input = create_random_query_interface(db)
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/queries/{form_input.id}",
        headers=normal_user_token_headers,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Query Interface read multi endpoint -------------------------------
# --------------------------------------------------------------------------------------


def test_read_multi_query_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully retrieve multiple interfaces"""
    form_inputs = [create_random_query_interface(db) for i in range(10)]
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/queries/",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    for form_input in form_inputs:
        found_match = False
        for stored_form_input in content["records"]:
            id_match = stored_form_input["id"] == form_input.id
            name_match = stored_form_input["name"] == form_input.name
            type_match = stored_form_input["interface_type"] == QUERY_INTERFACE_TYPE
            template_match = stored_form_input["template"] == form_input.template
            if id_match and name_match and type_match and template_match:
                found_match = True
                break
        assert found_match


def test_read_multi_query_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """Fail if the user is not a superuser"""
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/queries/",
        headers=normal_user_token_headers,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Query Interface update endpoint -----------------------------------
# --------------------------------------------------------------------------------------


def test_update_query_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully update a query interface"""
    query = create_random_query_interface(db)
    data = {"name": random_lower_string()}
    response = client.put(
        f"{settings.API_V1_STR}/interfaces/queries/{query.id}",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["name"] == data["name"]
    assert content["id"] == query.id
    assert content["interface_type"] == QUERY_INTERFACE_TYPE
    assert content["template"] == query.template
    assert content["refresh_interval"] == query.refresh_interval


def test_update_query_interface_fail_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the interface doesn't exist"""
    data = {"name": random_lower_string()}
    response = client.put(
        f"{settings.API_V1_STR}/interfaces/queries/{-1}",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find query."


def test_update_query_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """Fail if the user is not a superuser"""
    query = create_random_query_interface(db)
    data = {"name": random_lower_string()}
    response = client.put(
        f"{settings.API_V1_STR}/interfaces/queries/{query.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Query Interface delete endpoint ------------------------------
# --------------------------------------------------------------------------------------


def test_delete_query_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully delete a queryinterface"""
    query = create_random_query_interface(db)
    response = client.delete(
        f"{settings.API_V1_STR}/interfaces/queries/{query.id}",
        headers=superuser_token_headers,
    )
    stored_query = crud.query.get(db, id=query.id)
    content = response.json()
    assert response.status_code == 200
    assert content["name"] == query.name
    assert stored_query is None


def test_delete_query_interface_fail_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the query interface doesn't exist"""
    response = client.delete(
        f"{settings.API_V1_STR}/interfaces/queries/{-1}",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find query."


def test_delete_query_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """Fail if the user is not a superuser"""
    query = create_random_query_interface(db)
    response = client.delete(
        f"{settings.API_V1_STR}/interfaces/queries/{query.id}",
        headers=normal_user_token_headers,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Interface run query endpoint --------------------------------------
# --------------------------------------------------------------------------------------


def test_query_interface_run_query(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully run a query interface query"""
    query = create_random_query_interface(db)
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/queries/{query.id}/run",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert content


def test_query_interface_run_query_fail_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the query interface doesn't exist"""
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/queries/{-1}/run",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find query."


def test_query_interface_run_query_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully run a query interface query as a normal user"""
    setup = query_permission_setup(db, permission_type=PermissionTypeEnum.read)
    query = setup["query"]
    user = setup["user"]
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/queries/{query.id}/run",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert content


def test_query_interface_run_query_normal_user_fail_no_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the user doesn't have read permission for the interface"""
    setup = query_permission_setup(
        db, permission_type=PermissionTypeEnum.read, permission_enabled=False
    )
    query = setup["query"]
    user = setup["user"]
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/queries/{query.id}/run",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        f"User ID {user.id} does not have read permissions for "
        f"interface ID {query.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
