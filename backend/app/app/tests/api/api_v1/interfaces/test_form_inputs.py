from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.tests.utils.form_input import (
    create_random_form_input_interface,
    test_table_template,
)
from app.tests.utils.utils import random_lower_string


FORM_INPUT_INTERFACE_TYPE = "form_input_interface"

# --------------------------------------------------------------------------------------
# region | Tests for Form Input Interface create endpoint ------------------------------
# --------------------------------------------------------------------------------------


def test_create_form_input_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful interface creation"""
    data = {
        "name": random_lower_string(),
        "template": test_table_template().dict(),
    }
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/form-inputs/",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["name"] == data["name"]
    assert content["interface_type"] == FORM_INPUT_INTERFACE_TYPE
    assert content["template"] == data["template"]


def test_create_form_input_interface_fail_duplicate_table_name(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """
    Interface creation should fail if the template table_name already
    exists
    """
    name = random_lower_string()
    template = test_table_template().dict()
    form_input_in = schemas.FormInputCreate(name=name, template=template)
    crud.form_input.create(db=db, obj_in=form_input_in, created_by_id=1)
    data = {
        "name": name,
        "template": template,
    }
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/form-inputs/",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == (
        "A form input interface with that table name already exists, "
        "rename your template table."
    )


def test_create_form_input_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """If the user attempting to access the endpoint is not a superuser"""
    data = {
        "name": random_lower_string(),
        "template": test_table_template().dict(),
    }
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/form-inputs/",
        headers=normal_user_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Form Input Interface read one endpoint ----------------------------
# --------------------------------------------------------------------------------------


def test_read_form_input_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully retrieve a form input by ID"""
    form_input = create_random_form_input_interface(db)
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["id"] == form_input.id
    assert content["name"] == form_input.name
    assert content["interface_type"] == FORM_INPUT_INTERFACE_TYPE
    assert content["template"] == form_input.template


def test_read_form_input_interface_fail_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail when the form input interface doesn't exist"""
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{-1}",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_read_form_input_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """If the user attempting to access the endpoint is not a superuser"""
    form_input = create_random_form_input_interface(db)
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}",
        headers=normal_user_token_headers,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Form Input Interface read multi endpoint --------------------------
# --------------------------------------------------------------------------------------


def test_read_multi_form_input_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully retrieve multiple interfaces"""
    form_inputs = [create_random_form_input_interface(db) for i in range(10)]
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/form-inputs/",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    for form_input in form_inputs:
        found_match = False
        for stored_form_input in content:
            id_match = stored_form_input["id"] == form_input.id
            name_match = stored_form_input["name"] == form_input.name
            type_match = (
                stored_form_input["interface_type"] == FORM_INPUT_INTERFACE_TYPE
            )
            template_match = stored_form_input["template"] == form_input.template
            if id_match and name_match and type_match and template_match:
                found_match = True
                break
        assert found_match


def test_read_multi_form_input_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """Fail if the user is not a superuser"""
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/form-inputs/",
        headers=normal_user_token_headers,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Form Input Interface update endpoint ------------------------------
# --------------------------------------------------------------------------------------


def test_update_form_input_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully update a form input interface"""
    form_input = create_random_form_input_interface(db)
    data = {"name": random_lower_string()}
    response = client.put(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["name"] == data["name"]
    assert content["id"] == form_input.id
    assert content["interface_type"] == FORM_INPUT_INTERFACE_TYPE
    assert content["template"] == form_input.template


def test_update_form_input_interface_fail_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the interface doesn't exist"""
    data = {"name": random_lower_string()}
    response = client.put(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{-1}",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_update_form_input_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """Fail if the user is not a superuser"""
    form_input = create_random_form_input_interface(db)
    data = {"name": random_lower_string()}
    response = client.put(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


def test_update_form_input_interface_fail_table_created(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the table has already been created"""
    form_input = create_random_form_input_interface(db)
    crud.form_input.create_template_table(db, id=form_input.id)
    data = {"template": test_table_template().dict()}
    response = client.put(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}",
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
# region | Tests for Form Input Interface delete endpoint ------------------------------
# --------------------------------------------------------------------------------------


def test_delete_form_input_interface(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully delete a form input interface"""
    form_input = create_random_form_input_interface(db)
    response = client.delete(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}",
        headers=superuser_token_headers,
    )
    stored_interface = crud.form_input.get(db, id=form_input.id)
    content = response.json()
    assert response.status_code == 200
    assert content["name"] == form_input.name
    assert stored_interface is None


def test_delete_form_input_interface_fail_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the form input interface doesn't exist"""
    response = client.delete(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{-1}",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_delete_form_input_interface_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """Fail if the user is not a superuser"""
    form_input = create_random_form_input_interface(db)
    response = client.delete(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}",
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
    """Successfully build a form input interface's backing table"""
    form_input = create_random_form_input_interface(db)
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}/build_table",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["name"] == form_input.name
    assert content["table_created"]


def test_build_table_fail_interface_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the form input interface doesn't exist"""
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{-1}/build_table",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_build_table_fail_not_superuser(
    client: TestClient, normal_user_token_headers: dict, db: Session
) -> None:
    """Fail if the user is not a superuser"""
    form_input = create_random_form_input_interface(db)
    response = client.post(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}/build_table",
        headers=normal_user_token_headers,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for Interface read schema endpoint ------------------------------------
# --------------------------------------------------------------------------------------


def test_read_form_input_interface_schema(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully retrieve a form input interface schema"""
    table_name = "form_input_test_table"
    form_input = crud.form_input.get_by_template_table_name(db, table_name=table_name)
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}/schema",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["title"] == table_name


def test_read_form_input_interface_schema_fail_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail when the form input interface specified isn't in the database"""
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{-1}/schema",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_read_form_input_interface_schema_fail_table_not_created(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail when the backing table hasn't been created yet"""
    form_input = create_random_form_input_interface(db)
    response = client.get(
        f"{settings.API_V1_STR}/interfaces/form-inputs/{form_input.id}/schema",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        "The backing table for this interface has not been created."
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
