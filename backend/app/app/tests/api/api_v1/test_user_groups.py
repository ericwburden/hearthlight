from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.schemas import PermissionTypeEnum
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.node import create_random_node
from app.tests.utils.user import create_random_user
from app.tests.utils.user_group import create_random_user_group
from app.tests.utils.utils import random_lower_string
from app.tests.utils.setup import (
    node_permission_setup,
    user_group_permission_setup,
    multi_user_group_permission_setup,
)


# --------------------------------------------------------------------------------------
# region Tests for UserGroup create user group endpoint --------------------------------
# --------------------------------------------------------------------------------------


def test_create_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful UserGroup creation"""
    node = create_random_node(db, created_by_id=1, node_type="test_create_user_group")
    data = {"name": random_lower_string(), "node_id": node.id}
    response = client.post(
        f"{settings.API_V1_STR}/user_groups/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["node_id"] == data["node_id"]
    assert "id" in content
    assert "created_at" in content
    assert "updated_at" in content
    assert "created_by_id" in content
    assert "updated_by_id" in content


def test_create_user_group_normal_user(client: TestClient, db: Session) -> None:
    """Successfully create UserGroup with normal user"""

    setup = node_permission_setup(
        db,
        node_type="test_create_user_group_normal_user",
        permission_type=PermissionTypeEnum.create,
        permission_enabled=True,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    data = {"node_id": setup["node"].id, "name": random_lower_string()}
    response = client.post(
        f"{settings.API_V1_STR}/user_groups/", headers=user_token_headers, json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["node_id"] == data["node_id"]
    assert content["name"] == data["name"]
    assert "id" in content
    assert "created_at" in content
    assert "updated_at" in content
    assert "created_by_id" in content
    assert "updated_by_id" in content


def test_create_user_group_fail_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """UserGroup creation fails if the node doesn't exist"""
    data = {"name": random_lower_string(), "node_id": -100}
    response = client.post(
        f"{settings.API_V1_STR}/user_groups/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find node indicated by node_id."


def test_create_user_group_fail_inactive_node(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """UserGroup creation failes if the node is inactive"""
    node = create_random_node(
        db,
        created_by_id=1,
        node_type="test_create_user_group_fail_inactive_node",
        is_active=False,
    )
    data = {"name": random_lower_string(), "node_id": node.id}
    response = client.post(
        f"{settings.API_V1_STR}/user_groups/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Cannot add user group to an inactive node."


def test_create_user_group_fail_no_permission(client: TestClient, db: Session) -> None:
    """UserGroup creation fails without create permission on the node"""

    setup = node_permission_setup(
        db,
        node_type="test_create_user_group_normal_user",
        permission_type=PermissionTypeEnum.create,
        permission_enabled=False,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    data = {"node_id": setup["node"].id, "name": random_lower_string()}
    response = client.post(
        f"{settings.API_V1_STR}/user_groups/", headers=user_token_headers, json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "User does not have permission to create this node."


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for UserGroup create user group endpoint --------------------------------
# --------------------------------------------------------------------------------------


def test_read_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully read a user_group"""

    node = create_random_node(db, created_by_id=1, node_type="test_read_user_group")
    user_group = create_random_user_group(db, created_by_id=1, node_id=node.id)
    response = client.get(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == user_group.name
    assert content["node_id"] == user_group.node_id
    assert "id" in content
    assert "created_at" in content
    assert "updated_at" in content
    assert "created_by_id" in content
    assert "updated_by_id" in content


def test_read_user_group_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully read a user group with permissions"""

    setup = user_group_permission_setup(
        db, permission_type=PermissionTypeEnum.read, permission_enabled=True
    )

    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}",
        headers=user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["node_id"] == setup["user_group"].node_id
    assert content["name"] == setup["user_group"].name
    assert "id" in content
    assert "created_at" in content
    assert "updated_at" in content
    assert "created_by_id" in content
    assert "updated_by_id" in content


def test_read_user_group_fail_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the user group doesn't exist"""

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/{-1}", headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find user group."


def test_read_user_group_fail_no_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the user has no read permission on the user group"""

    setup = user_group_permission_setup(
        db, permission_type=PermissionTypeEnum.read, permission_enabled=False
    )

    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}",
        headers=user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == (
        f"User ID {setup['user'].id} does not have "
        f"read permissions for "
        f"user_group ID {setup['user_group'].id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for UserGroup read multi user group endpoint ----------------------------
# --------------------------------------------------------------------------------------


def test_read_user_groups(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully read multiple entered user groups"""

    node = create_random_node(db, created_by_id=1, node_type="test_read_user_group")
    user_groups = [
        create_random_user_group(db, created_by_id=1, node_id=node.id)
        for i in range(10)
    ]
    response = client.get(
        f"{settings.API_V1_STR}/user_groups/", headers=superuser_token_headers,
    )

    assert response.status_code == 200
    content = response.json()
    stored_user_group_ids = [user_group["id"] for user_group in content]
    assert len(content) >= 10
    assert all([ug.id in stored_user_group_ids for ug in user_groups])


def test_read_user_groups_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully read user groups with permissions"""

    setup = multi_user_group_permission_setup(
        db, n=10, permission_type=PermissionTypeEnum.read, permission_enabled=True,
    )
    user_group_ids = [user_group.id for user_group in setup["user_groups"]]
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/", headers=user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 10
    assert all([ug["id"] in user_group_ids for ug in content])


def test_read_user_groups_fail_no_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """A normal user with no permissions should fetch no user groups"""

    node = create_random_node(
        db, created_by_id=1, node_type="test_read_user_groups_fail_no_permission"
    )
    [create_random_user_group(db, created_by_id=1, node_id=node.id) for i in range(10)]
    user = create_random_user(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/user_groups/", headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert len(content) == 0


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for UserGroup update endpoint -------------------------------------------
# --------------------------------------------------------------------------------------


def test_update_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully update a user_group"""
    node = create_random_node(db, created_by_id=1, node_type="test_update_user_group")
    user_group = create_random_user_group(db, created_by_id=1, node_id=node.id)
    data = {"name": random_lower_string()}
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["node_id"] == user_group.node_id
    assert "id" in content
    assert "created_at" in content
    assert "updated_at" in content
    assert "created_by_id" in content
    assert "updated_by_id" in content


def test_update_user_group_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully update a user group as a normal user"""

    setup = user_group_permission_setup(
        db, permission_type=PermissionTypeEnum.update, permission_enabled=True
    )
    data = {"name": random_lower_string()}
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}",
        headers=user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["node_id"] == setup["user_group"].node_id
    assert "id" in content
    assert "created_at" in content
    assert "updated_at" in content
    assert "created_by_id" in content
    assert "updated_by_id" in content


def test_update_user_group_fail_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the specified user group doesn't exist in the database"""

    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{-1}",
        headers=superuser_token_headers,
        json={},
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find user group."


def test_update_user_group_fail_parent_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the node indicated by node_id doesn't exist in the database"""

    node = create_random_node(
        db, created_by_id=1, node_type="test_update_user_group_fail_parent_not_exists"
    )
    user_group = create_random_user_group(db, created_by_id=1, node_id=node.id)
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}",
        headers=superuser_token_headers,
        json={"node_id": -1},
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find input parent node."


def test_update_user_group_fail_user_no_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the user doesn't have update permissions on the target user group"""

    setup = user_group_permission_setup(
        db, permission_type=PermissionTypeEnum.update, permission_enabled=False
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}",
        headers=user_token_headers,
        json={"name": "no matter"},
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == (
        f"User ID {setup['user'].id} does not have "
        f"{setup['permission'].permission_type} permissions for "
        f"{setup['permission'].resource_type} ID {setup['user_group'].id}"
    )


def test_update_user_group_fail_user_no_parent_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the user doesn't have update permissions on the new parent node"""

    new_parent_node = create_random_node(
        db, created_by_id=1, node_type="new_parent_node"
    )
    data = {"node_id": new_parent_node.id}
    setup = user_group_permission_setup(
        db, permission_type=PermissionTypeEnum.update, permission_enabled=True
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}",
        headers=user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == (
        "User does not have permission to assign resources to node "
        f"{data['node_id']}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for UserGroup delete endpoint -------------------------------------------
# --------------------------------------------------------------------------------------


def test_delete_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully delete a user group"""

    node = create_random_node(db, created_by_id=1, node_type="test_delete_user_group")
    user_group = create_random_user_group(db, created_by_id=1, node_id=node.id)
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}", headers=superuser_token_headers
    )
    stored_user_group = crud.user_group.get(db, id=user_group.id)
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == user_group.name
    assert stored_user_group is None


def test_delete_user_group_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully delete a user group as a normal user"""

    setup = user_group_permission_setup(
        db,
        permission_type=PermissionTypeEnum.delete,
        permission_enabled=True,
    )
    breakpoint()
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}", headers=user_token_headers
    )
    stored_user_group = crud.user_group.get(db, id=setup["user_group"].id)
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == setup["user_group"].name
    assert stored_user_group is None


def test_delete_user_group_fail_user_group_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the specified user group doesn't exist in the database"""

    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{-1}", headers=superuser_token_headers, json={}
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find user group."


def test_delete_user_group_fail_user_no_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the user doesn't have delete permissions on the target user group"""

    setup = user_group_permission_setup(
        db,
        permission_type=PermissionTypeEnum.delete,
        permission_enabled=False,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}", headers=user_token_headers
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == (
        f"User ID {setup['user'].id} does not have "
        f"{setup['permission'].permission_type} permissions for "
        f"{setup['permission'].resource_type} ID {setup['user_group'].id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------

