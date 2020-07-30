from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.schemas import NodeCreate, PermissionTypeEnum
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.user_group import create_random_user_group
from app.tests.utils.utils import random_lower_string
from app.tests.utils.node import create_random_node

# --------------------------------------------------------------------------------------
# region Tests for Node create network endpoint ----------------------------------------
# --------------------------------------------------------------------------------------


def test_create_network(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful network creation"""
    data = {"node_type": "network", "name": random_lower_string(), "is_active": True}
    response = client.post(
        f"{settings.API_V1_STR}/nodes/", headers=superuser_token_headers, json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["node_type"] == data["node_type"]
    assert content["name"] == data["name"]
    assert content["is_active"]
    assert content["depth"] == 0
    assert "id" in content
    assert "parent_id" in content
    assert "created_at" in content
    assert "updated_at" in content
    assert "created_by_id" in content
    assert "updated_by_id" in content


def test_create_network_fail_with_parent(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Network creation should fail if a parent id is passed in"""
    parent_node = create_random_node(
        db, created_by_id=1, node_type="test_create_network_fail_with_parent"
    )
    data = {
        "node_type": "network",
        "name": random_lower_string(),
        "is_active": True,
        "parent_id": parent_node.id,
    }
    response = client.post(
        f"{settings.API_V1_STR}/nodes/", headers=superuser_token_headers, json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "New networks should not have a parent node"


def test_create_network_fail_not_superuser(client: TestClient, db: Session) -> None:
    """Network creation should fail if the user is not a superuser"""
    user = create_random_user(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    data = {"node_type": "network", "name": random_lower_string(), "is_active": True}
    response = client.post(
        f"{settings.API_V1_STR}/nodes/", headers=user_token_headers, json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Only superusers can create new networks."


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for Node create other node endpoint -------------------------------------
# --------------------------------------------------------------------------------------

def test_create_node(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful node creation"""
    parent_node = create_random_node(db, created_by_id=1, node_type="network")
    data = {
        "node_type": "test_create_node",
        "name": random_lower_string(),
        "is_active": True,
        "parent_id": parent_node.id,
    }
    response = client.post(
        f"{settings.API_V1_STR}/nodes/", headers=superuser_token_headers, json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["node_type"] == data["node_type"]
    assert content["name"] == data["name"]
    assert content["is_active"]
    assert content["parent_id"] == data["parent_id"]
    assert content["depth"] > 0
    assert "id" in content
    assert "created_at" in content
    assert "updated_at" in content
    assert "created_by_id" in content
    assert "updated_by_id" in content


def test_create_node_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful node creation by a normal user"""
    # Setup: Create the parent node, instantiate permissions, get create permission,
    # create user, create user group, add user to user group, give user group create
    # permission on the parent node
    parent_node = create_random_node(db, created_by_id=1, node_type="network")
    crud.node.instantiate_permissions(db, node=parent_node)
    permission = crud.node.get_permission(
        db, id=parent_node.id, permission_type=PermissionTypeEnum.create
    )
    user = create_random_user(db)
    user_group = create_random_user_group(db, created_by_id=1, node_id=parent_node.id)
    crud.user_group.add_user_to_group(db, user_group=user_group, user_id=user.id)
    crud.user_group.add_permission(db, user_group=user_group, permission=permission, enabled=True)

    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    data = {
        "node_type": "test_create_node",
        "name": random_lower_string(),
        "is_active": True,
        "parent_id": parent_node.id,
    }
    response = client.post(
        f"{settings.API_V1_STR}/nodes/", headers=user_token_headers, json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["node_type"] == data["node_type"]
    assert content["name"] == data["name"]
    assert content["is_active"]
    assert content["parent_id"] == data["parent_id"]
    assert content["depth"] > 0
    assert "id" in content
    assert "created_at" in content
    assert "updated_at" in content
    assert "created_by_id" in content
    assert "updated_by_id" in content


def test_create_node_fail_no_parent_provided(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Node creation should fail if no parent is provided"""
    data = {
        "node_type": "test_create_node",
        "name": random_lower_string(),
        "is_active": True,
    }
    response = client.post(
        f"{settings.API_V1_STR}/nodes/", headers=superuser_token_headers, json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Cannot create a node without a parent."


def test_create_node_fail_parent_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Node creation should fail if the parent id provided is for a nonexistent node"""
    data = {
        "node_type": "test_create_node",
        "name": random_lower_string(),
        "is_active": True,
        "parent_id": -1,
    }
    response = client.post(
        f"{settings.API_V1_STR}/nodes/", headers=superuser_token_headers, json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find node indicated by parent_id."
    

def test_create_node_fail_parent_not_active(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Node creation should fail if the parent node is not active"""
    parent_node = create_random_node(db, created_by_id=1, node_type="network", is_active=False)
    data = {
        "node_type": "test_create_node",
        "name": random_lower_string(),
        "is_active": True,
        "parent_id": parent_node.id,
    }
    response = client.post(
        f"{settings.API_V1_STR}/nodes/", headers=superuser_token_headers, json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Cannot add a node to an inactive parent."


def test_create_node_fail_permission_false(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Node creation fails when user has a permission not enabled for node parent"""
    # Setup: Create the parent node, instantiate permissions, get create permission,
    # create user, create user group, add user to user group, give user group create
    # permission on the parent node
    parent_node = create_random_node(db, created_by_id=1, node_type="network")
    crud.node.instantiate_permissions(db, node=parent_node)
    permission = crud.node.get_permission(
        db, id=parent_node.id, permission_type=PermissionTypeEnum.create
    )
    user = create_random_user(db)
    user_group = create_random_user_group(db, created_by_id=1, node_id=parent_node.id)
    crud.user_group.add_user_to_group(db, user_group=user_group, user_id=user.id)
    crud.user_group.add_permission(db, user_group=user_group, permission=permission, enabled=False)

    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    data = {
        "node_type": "test_create_node",
        "name": random_lower_string(),
        "is_active": True,
        "parent_id": parent_node.id,
    }
    response = client.post(
        f"{settings.API_V1_STR}/nodes/", headers=user_token_headers, json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "User does not have permission to create this node"


def test_create_node_fail_permission_missing(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Node creation fails when user does not have a permission associate with the resource"""
    # Setup: Create the parent node, create a user. Importantly, no permission setup
    # for the user and the parent node
    parent_node = create_random_node(db, created_by_id=1, node_type="network")
    user = create_random_user(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    data = {
        "node_type": "test_create_node",
        "name": random_lower_string(),
        "is_active": True,
        "parent_id": parent_node.id,
    }
    response = client.post(
        f"{settings.API_V1_STR}/nodes/", headers=user_token_headers, json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "User does not have permission to create this node"
