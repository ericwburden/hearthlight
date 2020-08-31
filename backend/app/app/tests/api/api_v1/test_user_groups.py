from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.crud.utils import model_encoder
from app.schemas import PermissionTypeEnum
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.node import create_random_node
from app.tests.utils.user import create_random_user
from app.tests.utils.user_group import create_random_user_group
from app.tests.utils.utils import random_lower_string
from app.tests.utils.setup import (
    node_permission_setup,
    node_all_permissions_setup,
    user_group_permission_setup,
    multi_user_group_permission_setup,
)

# ======================================================================================
# Tests for CRUD endpoints on the UserGroup itself =====================================
# ======================================================================================

# --------------------------------------------------------------------------------------
# region | Tests for UserGroup create user group endpoint ------------------------------
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
# region | Tests for UserGroup create user group endpoint ------------------------------
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
# region | Tests for UserGroup read multi user group endpoint --------------------------
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
# region | Tests for UserGroup update endpoint -----------------------------------------
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
# region | Tests for UserGroup delete endpoint -----------------------------------------
# --------------------------------------------------------------------------------------


def test_delete_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully delete a user group"""

    node = create_random_node(db, created_by_id=1, node_type="test_delete_user_group")
    user_group = create_random_user_group(db, created_by_id=1, node_id=node.id)
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}",
        headers=superuser_token_headers,
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
        db, permission_type=PermissionTypeEnum.delete, permission_enabled=True,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}",
        headers=user_token_headers,
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
        f"{settings.API_V1_STR}/user_groups/{-1}",
        headers=superuser_token_headers,
        json={},
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find user group."


def test_delete_user_group_fail_user_no_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the user doesn't have delete permissions on the target user group"""

    setup = user_group_permission_setup(
        db, permission_type=PermissionTypeEnum.delete, permission_enabled=False,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}",
        headers=user_token_headers,
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

# ======================================================================================
# Tests for endpoints to administer Permissions *in* UserGroups ========================
# ======================================================================================

# --------------------------------------------------------------------------------------
# region | Tests for UserGroup grant permission endpoint -------------------------------
# --------------------------------------------------------------------------------------


def test_user_group_grant_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully grant a permission to a user group"""
    node = create_random_node(db, node_type="test_user_group_grant_permission")
    user_group = create_random_user_group(db, node_id=node.id)
    permission = crud.node.get_permission(
        db, id=node.id, permission_type=PermissionTypeEnum.read
    )
    response = client.put(
        (
            f"{settings.API_V1_STR}/user_groups/{user_group.id}"
            f"/permissions/{permission.id}"
        ),
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["msg"] == (
        f"Granted UserGroup {user_group.id} '{permission.permission_type}'"
        f"permission on {permission.resource_type} {node.id}"
    )


def test_user_group_grant_permission_normal_user(
    client: TestClient, db: Session
) -> None:
    """Successfully add a permission to a user group as a normal user"""
    setup = user_group_permission_setup(
        db, permission_type=PermissionTypeEnum.update, permission_enabled=True
    )
    delete_permission = crud.node.get_permission(
        db, id=setup["node"].id, permission_type=PermissionTypeEnum.delete
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.put(
        (
            f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}"
            f"/permissions/{delete_permission.id}"
        ),
        headers=user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["msg"] == (
        f"Granted UserGroup {setup['user_group'].id} "
        f"'{delete_permission.permission_type}'"
        f"permission on {delete_permission.resource_type} {setup['node'].id}"
    )


def test_user_group_grant_permission_fail_no_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(
        db,
        created_by_id=1,
        node_type="test_user_group_grant_permission_fail_no_user_group",
    )
    permission = crud.node.get_permission(
        db, id=node.id, permission_type=PermissionTypeEnum.read
    )
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{-1}/permissions/{permission.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find user group."


def test_user_group_grant_permission_fail_no_permission_in_db(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(
        db,
        created_by_id=1,
        node_type="test_user_group_grant_permission_fail_no_user_group",
    )
    user_group = create_random_user_group(db, created_by_id=1, node_id=node.id)
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/permissions/{-1}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find permission."


def test_user_group_grant_permission_fail_depth_mismatch(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    other_node = create_random_node(db, created_by_id=1, node_type="not_descended")
    root_node = create_random_node(db, created_by_id=1, node_type="root_node")
    user_group = create_random_user_group(db, created_by_id=1, node_id=root_node.id)
    permission = crud.node.get_permission(
        db, id=other_node.id, permission_type=PermissionTypeEnum.update
    )
    response = client.put(
        (
            f"{settings.API_V1_STR}/user_groups/{user_group.id}"
            f"/permissions/{permission.id}"
        ),
        headers=superuser_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == (
        f"{permission.resource_type} {other_node.id} is not descended from node "
        f"{root_node.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for UserGroup bulk grant permission endpoint --------------------------
# --------------------------------------------------------------------------------------


def test_user_group_grant_bulk_permissions(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully grant multiple permissions to a user group"""
    node = create_random_node(
        db, created_by_id=1, node_type="test_user_group_grant_bulk_permission"
    )
    user_group = create_random_user_group(db, created_by_id=1, node_id=node.id)
    permissions = crud.node.get_permissions(db, id=node.id)
    data = [model_encoder(p) for p in permissions]
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/permissions/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["msg"] == (
        f"Granted {len(permissions)} permissions to UserGroup {user_group.id}."
    )


def test_user_group_grant_bulk_permissions_normal_user(
    client: TestClient, db: Session
) -> None:
    """Successfully add multiple permissions to a user group as a normal user"""
    setup = user_group_permission_setup(
        db, permission_type=PermissionTypeEnum.update, permission_enabled=True
    )
    permissions = crud.node.get_permissions(db, id=setup["node"].id)
    data = [model_encoder(p) for p in permissions]
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}/permissions/",
        headers=user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["msg"] == (
        f"Granted {len(permissions)} permissions to UserGroup {setup['user_group'].id}."
    )


def test_user_group_grant_multiple_permissions_fail_no_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(
        db, created_by_id=1, node_type="test_user_group_grant_bulk_permission"
    )
    permissions = crud.node.get_permissions(db, id=node.id)
    data = [model_encoder(p) for p in permissions]
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{-1}/permissions/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find user group."


def test_user_group_grant_multiple_permissions_fail_missing_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(
        db,
        created_by_id=1,
        node_type="grant_multiple_permissions_fail_missing_permission",
    )
    user_group = create_random_user_group(db, created_by_id=1, node_id=node.id)
    permissions = crud.node.get_permissions(db, id=node.id)
    data = [model_encoder(p) for p in permissions]
    for p in permissions:
        crud.permission.remove(db, id=p.id)
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/permissions/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find one or more permissions."


def test_user_group_grant_multiple_permissions_fail_depth_mismatch(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    other_node1 = create_random_node(db, created_by_id=1, node_type="not_descended")
    other_node2 = create_random_node(db, created_by_id=1, node_type="not_descended")
    root_node = create_random_node(db, created_by_id=1, node_type="root_node")
    user_group = create_random_user_group(db, created_by_id=1, node_id=root_node.id)
    permissions = [
        *crud.node.get_permissions(db, id=other_node1.id),
        *crud.node.get_permissions(db, id=other_node2.id),
    ]
    data = [model_encoder(p) for p in permissions]
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/permissions/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    expected_detail = f"One or more permissions not descended from node {root_node.id}"
    assert content["detail"] == expected_detail


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for UserGroup revoke permission endpoint ------------------------------
# --------------------------------------------------------------------------------------


def test_user_group_revoke_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully revoke a permission from a user group"""
    setup = node_permission_setup(
        db,
        node_type="test_user_group_revoke_permission",
        permission_type=PermissionTypeEnum.update,
        permission_enabled=True,
    )
    response = client.delete(
        (
            f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}"
            f"/permissions/{setup['permission'].id}"
        ),
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["msg"] == (
        f"Revoked '{setup['permission'].permission_type}' permission for "
        f"{setup['permission'].resource_type} {setup['node'].id} in "
        f"UserGroup {setup['user_group'].id}"
    )


def test_user_group_revoke_permission_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """
    Successfully revoke a permission from a user group with a normal
    user
    """
    setup = node_permission_setup(
        db,
        node_type="test_user_group_revoke_permission",
        permission_type=PermissionTypeEnum.update,
        permission_enabled=True,
    )
    user_group_update_permission = crud.user_group.get_permission(
        db, id=setup["user_group"].id, permission_type=PermissionTypeEnum.update
    )
    crud.permission.grant(
        db,
        user_group_id=setup["user_group"].id,
        permission_id=user_group_update_permission.id,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.delete(
        (
            f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}"
            f"/permissions/{setup['permission'].id}"
        ),
        headers=user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["msg"] == (
        f"Revoked '{setup['permission'].permission_type}' permission for "
        f"{setup['permission'].resource_type} {setup['node'].id} in "
        f"UserGroup {setup['user_group'].id}"
    )


def test_user_group_revoke_permission_fail_no_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(
        db,
        created_by_id=1,
        node_type="test_user_group_grant_permission_fail_no_user_group",
    )
    permission = crud.node.get_permission(
        db, id=node.id, permission_type=PermissionTypeEnum.read
    )
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{-1}/permissions/{permission.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find user group."


def test_user_group_revoke_permission_fail_no_permission_in_db(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(
        db,
        created_by_id=1,
        node_type="test_user_group_revoke_permission_fail_no_permission_in_db",
    )
    user_group = create_random_user_group(db, created_by_id=1, node_id=node.id)
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/permissions/{-1}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find permission."


def test_user_group_revoke_permission_fail_not_in_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(
        db,
        created_by_id=1,
        node_type="test_user_group_grant_permission_fail_no_user_group",
    )
    user_group = create_random_user_group(db, created_by_id=1, node_id=node.id)
    permission = crud.node.get_permission(
        db, id=node.id, permission_type=PermissionTypeEnum.read
    )
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/permissions/{permission.id}",  # noqa: E501
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Permission not in user group."


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for UserGroup revoke permission endpoint ------------------------------
# --------------------------------------------------------------------------------------


def test_user_group_revoke_bulk_permissions(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully revoke multiple permissions from a user group"""
    setup = node_all_permissions_setup(db)
    permissions = crud.node.get_permissions(db, id=setup["node"].id)
    data = [model_encoder(p) for p in permissions]
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}/permissions/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["msg"] == (
        f"Revoked {len(permissions)} permissions in UserGroup {setup['user_group'].id}."
    )


def test_user_group_revoke_bulk_permissions_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully revoke multiple permissions from a user group"""
    setup = node_all_permissions_setup(db)
    permissions = crud.node.get_permissions(db, id=setup["node"].id)
    user_group_update_permission = crud.user_group.get_permission(
        db, id=setup["user_group"].id, permission_type=PermissionTypeEnum.update
    )
    crud.permission.grant(
        db,
        user_group_id=setup["user_group"].id,
        permission_id=user_group_update_permission.id,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    data = [model_encoder(p) for p in permissions]
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}/permissions/",
        headers=user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["msg"] == (
        f"Revoked {len(permissions)} permissions in UserGroup {setup['user_group'].id}."
    )


def test_user_group_revoke_multiple_permissions_fail_no_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    setup = node_all_permissions_setup(db)
    permissions = crud.node.get_permissions(db, id=setup["node"].id)
    data = [model_encoder(p) for p in permissions]
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{-1}/permissions/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find user group."


def test_user_group_revoke_multiple_permissions_fail_no_permission_in_db(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    setup = node_all_permissions_setup(db)
    permissions = crud.node.get_permissions(db, id=setup["node"].id)
    data = [model_encoder(p) for p in permissions]
    [crud.permission.remove(db, id=p.id) for p in permissions]
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}/permissions/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find one or more permissions."


def test_user_group_revoke_multiple_permissions_fail_not_in_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    setup = node_all_permissions_setup(db)
    node = create_random_node(db, created_by_id=-1, node_type="not_related")
    permissions = crud.node.get_permissions(db, id=node.id)
    data = [model_encoder(p) for p in permissions]
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{setup['user_group'].id}/permissions/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "One or more permissions not in user group."


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------

# ======================================================================================
# Tests for endpoints to manage Users in UserGroups ====================================
# ======================================================================================

# --------------------------------------------------------------------------------------
# region | Tests for UserGroup add user endpoint ---------------------------------------
# --------------------------------------------------------------------------------------


def test_user_group_add_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(db, node_type="test_user_group_add_user")
    user_group = create_random_user_group(db, node_id=node.id)
    new_user = create_random_user(db)

    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/{new_user.id}",
        headers=superuser_token_headers,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 200
    assert content["user_group_id"] == user_group.id
    assert content["user_id"] == new_user.id


def test_user_group_add_user_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    setup = user_group_permission_setup(
        db, permission_type=PermissionTypeEnum.update, permission_enabled=True
    )
    user_group = setup["user_group"]
    new_user = create_random_user(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/{new_user.id}",
        headers=user_token_headers,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 200
    assert content["user_group_id"] == user_group.id
    assert content["user_id"] == new_user.id


def test_user_group_add_user_fail_no_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    new_user = create_random_user(db)

    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{-1}/users/{new_user.id}",
        headers=superuser_token_headers,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 404
    assert content["detail"] == "Can not find user group."


def test_user_group_add_user_fail_no_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(db, node_type="test_user_group_add_user")
    user_group = create_random_user_group(db, node_id=node.id)

    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/{-1}",
        headers=superuser_token_headers,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 404
    assert content["detail"] == "Can not find user."


def test_user_group_add_user_normal_user_fail_no_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(
        db, node_type="test_user_group_add_user_normal_user_fail_no_permission"
    )
    user_group = create_random_user_group(db, node_id=node.id)
    user = create_random_user(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/{user.id}",
        headers=user_token_headers,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 403
    assert content["detail"] == (
        f"User ID {user.id} does not have update permissions for "
        f"user_group ID {user_group.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for UserGroup add multiple users endpoint -----------------------------
# --------------------------------------------------------------------------------------


def test_user_group_add_multiple_users(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(db, node_type="test_user_group_add_user")
    user_group = create_random_user_group(db, node_id=node.id)
    users = [create_random_user(db) for i in range(10)]
    user_ids = [user.id for user in users]

    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/",
        headers=superuser_token_headers,
        json=user_ids,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 200
    for u in content:
        assert u["user_id"] in user_ids


def test_user_group_add_multiple_users_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    setup = user_group_permission_setup(
        db, permission_type=PermissionTypeEnum.update, permission_enabled=True
    )
    user_group = setup["user_group"]
    users = [create_random_user(db) for i in range(10)]
    user_ids = [user.id for user in users]
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/",
        headers=user_token_headers,
        json=user_ids,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 200
    for u in content:
        assert u["user_id"] in user_ids


def test_user_group_add_multiple_users_fail_no_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    users = [create_random_user(db) for i in range(10)]
    user_ids = [user.id for user in users]

    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{-1}/users/",
        headers=superuser_token_headers,
        json=user_ids,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 404
    assert content["detail"] == "Can not find user group."


def test_user_group_add_multiple_users_fail_no_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(db, node_type="test_user_group_add_user")
    user_group = create_random_user_group(db, node_id=node.id)
    user = create_random_user(db)

    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/",
        headers=superuser_token_headers,
        json=[-1, -2, -3, user.id],
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 404
    assert content["detail"] == "Can not find one or more users."


def test_user_group_add_multiple_users_normal_user_fail_no_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(
        db, node_type="test_user_group_add_user_normal_user_fail_no_permission"
    )
    user_group = create_random_user_group(db, node_id=node.id)
    users = [create_random_user(db) for i in range(10)]
    user_ids = [user.id for user in users]
    user_token_headers = authentication_token_from_email(
        client=client, email=users[0].email, db=db
    )
    response = client.put(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/",
        headers=user_token_headers,
        json=user_ids,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 403
    assert content["detail"] == (
        f"User ID {users[0].id} does not have update permissions for "
        f"user_group ID {user_group.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for UserGroup remove user endpoint ------------------------------------
# --------------------------------------------------------------------------------------


def test_user_group_remove_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(db, node_type="test_user_group_remove_user")
    user_group = create_random_user_group(db, node_id=node.id)
    user = create_random_user(db)
    crud.user_group.add_user(db, user_group=user_group, user_id=user.id)

    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/{user.id}",
        headers=superuser_token_headers,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 200
    assert content["id"] == user.id


def test_user_group_remove_user_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    setup = user_group_permission_setup(
        db, permission_type=PermissionTypeEnum.update, permission_enabled=True
    )
    user_group = setup["user_group"]
    user = create_random_user(db)
    crud.user_group.add_user(db, user_group=user_group, user_id=user.id)

    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/{user.id}",
        headers=user_token_headers,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 200
    assert content["id"] == user.id


def test_user_group_remove_user_fail_no_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    new_user = create_random_user(db)

    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{-1}/users/{new_user.id}",
        headers=superuser_token_headers,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 404
    assert content["detail"] == "Can not find user group."


def test_user_group_remove_user_fail_no_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(db, node_type="test_user_group_remove_user_fail_no_user")
    user_group = create_random_user_group(db, node_id=node.id)

    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/{-1}",
        headers=superuser_token_headers,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 404
    assert content["detail"] == "Can not find user."


def test_user_group_remove_user_fail_user_not_in_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(
        db, node_type="test_user_group_remove_user_fail_user_not_in_group"
    )
    user_group = create_random_user_group(db, node_id=node.id)
    user = create_random_user(db)

    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/{user.id}",
        headers=superuser_token_headers,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 404
    assert content["detail"] == f"User {user.id} not in user group {user_group.id}"


def test_user_group_remove_user_normal_user_fail_no_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(
        db, node_type="test_user_group_remove_user_normal_user_fail_no_permission"
    )
    user_group = create_random_user_group(db, node_id=node.id)
    user = create_random_user(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/{user.id}",
        headers=user_token_headers,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 403
    assert content["detail"] == (
        f"User ID {user.id} does not have update permissions for "
        f"user_group ID {user_group.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for UserGroup remove multiple users endpoint --------------------------
# --------------------------------------------------------------------------------------


def test_user_group_remove_multiple_users(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(db, node_type="test_user_group_remove_user")
    user_group = create_random_user_group(db, node_id=node.id)
    users = [create_random_user(db) for i in range(10)]
    user_ids = [user.id for user in users]
    crud.user_group.add_users(db, user_group=user_group, user_ids=user_ids)

    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/",
        headers=superuser_token_headers,
        json=user_ids,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 200
    for returned_user in content:
        assert returned_user['id'] in user_ids


def test_user_group_remove_multiple_users_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    setup = user_group_permission_setup(
        db, permission_type=PermissionTypeEnum.update, permission_enabled=True
    )
    user_group = setup["user_group"]
    users = [create_random_user(db) for i in range(10)]
    user_ids = [user.id for user in users]
    crud.user_group.add_users(db, user_group=user_group, user_ids=user_ids)

    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/",
        headers=user_token_headers,
        json=user_ids,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 200
    for returned_user in content:
        assert returned_user['id'] in user_ids


def test_user_group_remove_multiple_users_fail_no_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    users = [create_random_user(db) for i in range(10)]
    user_ids = [user.id for user in users]

    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{-1}/users/",
        headers=superuser_token_headers,
        json=user_ids,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 404
    assert content["detail"] == "Can not find user group."


def test_user_group_remove_multiple_users_fail_no_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(db, node_type="test_user_group_remove_user")
    user_group = create_random_user_group(db, node_id=node.id)
    user = create_random_user(db)

    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/",
        headers=superuser_token_headers,
        json=[-1, -2, -3, user.id],
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 404
    assert content["detail"] == "Can not find one or more users."


def test_user_group_remove_multiple_users_fail_user_not_in_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(
        db, node_type="test_user_group_remove_user_fail_user_not_in_group"
    )
    user_group = create_random_user_group(db, node_id=node.id)
    users = [create_random_user(db) for i in range(10)]
    user_ids = [user.id for user in users]

    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/",
        headers=superuser_token_headers,
        json=user_ids,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 404
    assert content["detail"] in (
        f"User {user.id} not in user group {user_group.id}" for user in users
    )


def test_user_group_remove_multiple_users_normal_user_fail_no_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    node = create_random_node(
        db, node_type="test_user_group_remove_user_normal_user_fail_no_permission"
    )
    user_group = create_random_user_group(db, node_id=node.id)
    users = [create_random_user(db) for i in range(10)]
    user_ids = [user.id for user in users]
    crud.user_group.add_users(db, user_group=user_group, user_ids=user_ids)
    user_token_headers = authentication_token_from_email(
        client=client, email=users[0].email, db=db
    )
    response = client.delete(
        f"{settings.API_V1_STR}/user_groups/{user_group.id}/users/",
        headers=user_token_headers,
        json=user_ids,
    )

    response_status = response.status_code
    content = response.json()
    assert response_status == 403
    assert content["detail"] == (
        f"User ID {users[0].id} does not have update permissions for "
        f"user_group ID {user_group.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
