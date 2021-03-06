from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.schemas import PermissionTypeEnum
from app.tests.utils.form_input import create_random_form_input_interface
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import random_lower_string
from app.tests.utils.node import create_random_node
from app.tests.utils.setup import (
    node_permission_setup,
    multi_node_permission_setup,
    node_children_setup,
)

# --------------------------------------------------------------------------------------
# region Tests for Node create network endpoint ----------------------------------------
# --------------------------------------------------------------------------------------


def test_create_network(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful network creation"""
    data = {"node_type": "network", "name": random_lower_string(), "is_active": True}
    response = client.post(
        f"{settings.API_V1_STR}/nodes/",
        headers=superuser_token_headers,
        json=data,
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
        f"{settings.API_V1_STR}/nodes/",
        headers=superuser_token_headers,
        json=data,
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
        f"{settings.API_V1_STR}/nodes/",
        headers=user_token_headers,
        json=data,
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
        f"{settings.API_V1_STR}/nodes/",
        headers=superuser_token_headers,
        json=data,
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

    setup = node_permission_setup(
        db,
        node_type="test_create_node_normal_user",
        permission_type=PermissionTypeEnum.create,
        permission_enabled=True,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    data = {
        "node_type": "test_create_node",
        "name": random_lower_string(),
        "is_active": True,
        "parent_id": setup["node"].id,
    }
    response = client.post(
        f"{settings.API_V1_STR}/nodes/",
        headers=user_token_headers,
        json=data,
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
        f"{settings.API_V1_STR}/nodes/",
        headers=superuser_token_headers,
        json=data,
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
        f"{settings.API_V1_STR}/nodes/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find node indicated by parent_id."


def test_create_node_fail_parent_not_active(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Node creation should fail if the parent node is not active"""
    parent_node = create_random_node(
        db, created_by_id=1, node_type="network", is_active=False
    )
    data = {
        "node_type": "test_create_node",
        "name": random_lower_string(),
        "is_active": True,
        "parent_id": parent_node.id,
    }
    response = client.post(
        f"{settings.API_V1_STR}/nodes/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Cannot add a node to an inactive parent."


def test_create_node_fail_permission_false(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Node creation fails when user has a permission not enabled for node parent"""

    setup = node_permission_setup(
        db,
        node_type="test_create_node_fail_permission_false",
        permission_type=PermissionTypeEnum.create,
        permission_enabled=False,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    data = {
        "node_type": "test_create_node",
        "name": random_lower_string(),
        "is_active": True,
        "parent_id": setup["node"].id,
    }
    response = client.post(
        f"{settings.API_V1_STR}/nodes/",
        headers=user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "User does not have permission to create this node"


def test_create_node_fail_permission_missing(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """
    Node creation fails when user does not have a permission associate
    with the resource
    """
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
        f"{settings.API_V1_STR}/nodes/",
        headers=user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "User does not have permission to create this node"


def test_create_node_fail_name_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the node name isn't unique"""
    existing_node = create_random_node(db)
    parent_node = create_random_node(db, created_by_id=1, node_type="network")
    data = {
        "node_type": "test_create_node",
        "name": existing_node.name,
        "is_active": True,
        "parent_id": parent_node.id,
    }
    response = client.post(
        f"{settings.API_V1_STR}/nodes/",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 409
    assert content["detail"] == "A node with that name already exists."


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for Node read one endpoint ----------------------------------------------
# --------------------------------------------------------------------------------------


def test_read_node(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully read a node"""

    node = create_random_node(db, created_by_id=1, node_type="network")
    response = client.get(
        f"{settings.API_V1_STR}/nodes/{node.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["node_type"] == node.node_type
    assert content["name"] == node.name
    assert content["is_active"]
    assert content["depth"] == 0
    assert "id" in content
    assert "parent_id" in content
    assert "created_at" in content
    assert "updated_at" in content
    assert "created_by_id" in content
    assert "updated_by_id" in content


def test_read_node_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully read a node with permissions"""

    setup = node_permission_setup(
        db,
        node_type="test_read_node_normal_user",
        permission_type=PermissionTypeEnum.read,
        permission_enabled=True,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/nodes/{setup['node'].id}",
        headers=user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["node_type"] == setup["node"].node_type
    assert content["name"] == setup["node"].name
    assert content["is_active"]
    assert content["depth"] == 0
    assert "id" in content
    assert "parent_id" in content
    assert "created_at" in content
    assert "updated_at" in content
    assert "created_by_id" in content
    assert "updated_by_id" in content


def test_read_node_fail_node_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the node doesn't exist"""

    response = client.get(
        f"{settings.API_V1_STR}/nodes/{-1}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find node."


def test_read_node_fail_node_no_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the user has no read permission on the node"""

    setup = node_permission_setup(
        db,
        node_type="test_read_node_fail_node_no_permission",
        permission_type=PermissionTypeEnum.read,
        permission_enabled=False,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/nodes/{setup['node'].id}",
        headers=user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == (
        f"User ID {setup['user'].id} does not have "
        f"read permissions for "
        f"node ID {setup['node'].id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for Node read multi endpoint --------------------------------------------
# --------------------------------------------------------------------------------------


def test_read_nodes(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully read multiple entered nodes"""

    nodes = [
        create_random_node(db, created_by_id=1, node_type="network") for i in range(10)
    ]
    response = client.get(
        f"{settings.API_V1_STR}/nodes/",
        headers=superuser_token_headers,
    )
    content = response.json()
    stored_node_ids = [node["id"] for node in content["records"]]
    assert response.status_code == 200
    assert len(content["records"]) >= 10
    assert all([n.id in stored_node_ids for n in nodes])


def test_read_nodes_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully read nodes with permissions"""

    setup = multi_node_permission_setup(
        db,
        n=10,
        node_type="test_read_nodes_normal_user",
        permission_type=PermissionTypeEnum.read,
        permission_enabled=True,
    )
    node_ids = [node.id for node in setup["nodes"]]
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/nodes/",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert len(content["records"]) == 10
    assert all([n["id"] in node_ids for n in content["records"]])


def test_read_nodes_fail_no_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """A normal user with no permissions should fetch no nodes"""

    [
        create_random_node(
            db, created_by_id=1, node_type="test_read_nodes_fail_no_permission"
        )
        for i in range(10)
    ]
    user = create_random_user(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/nodes/",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    assert len(content["records"]) == 0


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for Node read multi networks endpoint -----------------------------------
# --------------------------------------------------------------------------------------


def test_read_network_nodes(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully read multiple entered nodes"""

    nodes = [
        create_random_node(db, created_by_id=1, node_type="network") for i in range(10)
    ]
    response = client.get(
        f"{settings.API_V1_STR}/nodes/networks/",
        headers=superuser_token_headers,
    )
    content = response.json()
    stored_node_ids = [node["id"] for node in content["records"]]
    assert response.status_code == 200
    assert len(content["records"]) >= 10
    assert all([n.id in stored_node_ids for n in nodes])


def test_read_network_nodes_fail_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail when attempting to read network nodes as a normal user"""

    setup = multi_node_permission_setup(
        db,
        n=10,
        node_type="network",
        permission_type=PermissionTypeEnum.read,
        permission_enabled=True,
    )
    nodes = setup["nodes"]
    user = setup["user"]
    node_ids = [node.id for node in nodes]
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.get(
        f"{settings.API_V1_STR}/nodes/networks/",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "The user is not a superuser"


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for Node update endpoint ------------------------------------------------
# --------------------------------------------------------------------------------------


def test_update_node(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully update a node"""

    node = create_random_node(db, created_by_id=1, node_type="test_update_node")
    data = {
        "node_type": "updated_test_node",
        "name": random_lower_string(),
    }
    response = client.put(
        f"{settings.API_V1_STR}/nodes/{node.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["node_type"] == data["node_type"]
    assert content["name"] == data["name"]
    assert content["is_active"] == node.is_active
    assert content["parent_id"] == node.parent_id
    assert content["depth"] == 0
    assert "id" in content
    assert "created_at" in content
    assert "updated_at" in content
    assert "created_by_id" in content
    assert "updated_by_id" in content


def test_update_node_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully update a node as a normal user"""

    setup = node_permission_setup(
        db,
        node_type="test_update_node_normal_user",
        permission_type=PermissionTypeEnum.update,
        permission_enabled=True,
    )
    data = {
        "node_type": "updated_test_node",
        "name": random_lower_string(),
    }
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.put(
        f"{settings.API_V1_STR}/nodes/{setup['node'].id}",
        headers=user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["node_type"] == data["node_type"]
    assert content["name"] == data["name"]
    assert content["is_active"] == setup["node"].is_active
    assert content["parent_id"] == setup["node"].parent_id
    assert content["depth"] == 0
    assert "id" in content
    assert "created_at" in content
    assert "updated_at" in content
    assert "created_by_id" in content
    assert "updated_by_id" in content


def test_update_node_fail_node_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the specified node doesn't exist in the database"""

    response = client.put(
        f"{settings.API_V1_STR}/nodes/{-1}", headers=superuser_token_headers, json={}
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find node."


def test_update_node_fail_parent_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the node indicated by parent_id doesn't exist in the database"""

    node = create_random_node(
        db, created_by_id=1, node_type="test_update_node_fail_parent_not_exists"
    )
    response = client.put(
        f"{settings.API_V1_STR}/nodes/{node.id}",
        headers=superuser_token_headers,
        json={"parent_id": -1},
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find parent node."


def test_update_node_fail_user_no_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the user doesn't have update permissions on the target node"""

    setup = node_permission_setup(
        db,
        node_type="test_update_node_fail_user_no_permission",
        permission_type=PermissionTypeEnum.update,
        permission_enabled=False,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    data = {"name": "no matter"}
    response = client.put(
        f"{settings.API_V1_STR}/nodes/{setup['node'].id}",
        headers=user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == (
        f"User ID {setup['user'].id} does not have "
        f"{setup['permission'].permission_type} permissions for "
        f"{setup['permission'].resource_type} ID {setup['node'].id}"
    )


def test_update_node_fail_user_no_parent_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the user doesn't have update permissions on the new parent node"""

    new_parent_node = create_random_node(
        db, created_by_id=1, node_type="new_parent_node"
    )
    data = {"parent_id": new_parent_node.id}
    setup = node_permission_setup(
        db,
        node_type="test_update_node_fail_user_no_permission",
        permission_type=PermissionTypeEnum.update,
        permission_enabled=True,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.put(
        f"{settings.API_V1_STR}/nodes/{setup['node'].id}",
        headers=user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == (
        "User does not have permission to assign resources to node "
        f"{data['parent_id']}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for Node delete endpoint ------------------------------------------------
# --------------------------------------------------------------------------------------


def test_delete_node(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully delete a node"""

    node = create_random_node(db, created_by_id=1, node_type="test_delete_node")
    response = client.delete(
        f"{settings.API_V1_STR}/nodes/{node.id}", headers=superuser_token_headers
    )
    stored_node = crud.node.get(db, id=node.id)
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == node.name
    assert stored_node is None


def test_delete_node_normal_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully delete a node as a normal user"""

    setup = node_permission_setup(
        db,
        node_type="test_delete_node_normal_user",
        permission_type=PermissionTypeEnum.delete,
        permission_enabled=True,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.delete(
        f"{settings.API_V1_STR}/nodes/{setup['node'].id}", headers=user_token_headers
    )
    stored_node = crud.node.get(db, id=setup["node"].id)
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == setup["node"].name
    assert stored_node is None


def test_delete_node_fail_node_not_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the specified node doesn't exist in the database"""

    response = client.delete(
        f"{settings.API_V1_STR}/nodes/{-1}", headers=superuser_token_headers, json={}
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Cannot find node."


def test_delete_node_fail_user_no_permission(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fails if the user doesn't have delete permissions on the target node"""

    setup = node_permission_setup(
        db,
        node_type="test_delete_node_fail_user_no_permission",
        permission_type=PermissionTypeEnum.delete,
        permission_enabled=False,
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=setup["user"].email, db=db
    )
    response = client.delete(
        f"{settings.API_V1_STR}/nodes/{setup['node'].id}", headers=user_token_headers
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == (
        f"User ID {setup['user'].id} does not have "
        f"{setup['permission'].permission_type} permissions for "
        f"{setup['permission'].resource_type} ID {setup['node'].id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for Node add interface endpoint -----------------------------------------
# --------------------------------------------------------------------------------------


def test_add_interface_to_node(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully add an interface to a node"""

    node = create_random_node(db)
    interface = create_random_form_input_interface(db)
    response = client.post(
        f"{settings.API_V1_STR}/nodes/{node.id}/interfaces/{interface.id}/add",
        headers=superuser_token_headers,
    )
    db.refresh(node)
    assert response.status_code == 200
    assert interface in node.interfaces


def test_add_interface_to_node_fail_node_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the node doesn't exist"""

    interface = create_random_form_input_interface(db)
    response = client.post(
        f"{settings.API_V1_STR}/nodes/{-1}/interfaces/{interface.id}/add",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find node."


def test_add_interface_to_node_fail_interface_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the interface doesn't exist"""

    node = create_random_node(db)
    response = client.post(
        f"{settings.API_V1_STR}/nodes/{node.id}/interfaces/{-1}/add",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_add_interface_to_node_normal_user(client: TestClient, db: Session) -> None:
    """Successfully add an interface to a node as a normal user"""

    setup = node_permission_setup(
        db,
        node_type="test",
        permission_type=PermissionTypeEnum.create,
        permission_enabled=True,
    )
    node = setup["node"]
    user = setup["user"]
    interface = create_random_form_input_interface(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.post(
        f"{settings.API_V1_STR}/nodes/{node.id}/interfaces/{interface.id}/add",
        headers=user_token_headers,
    )
    db.refresh(node)
    assert response.status_code == 200
    assert interface in node.interfaces


def test_add_interface_to_node_normal_user_fail_no_permission(
    client: TestClient, db: Session
) -> None:
    """Successfully add an interface to a node as a normal user"""

    setup = node_permission_setup(
        db,
        node_type="test",
        permission_type=PermissionTypeEnum.create,
        permission_enabled=False,
    )
    node = setup["node"]
    user = setup["user"]
    interface = create_random_form_input_interface(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.post(
        f"{settings.API_V1_STR}/nodes/{node.id}/interfaces/{interface.id}/add",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        f"User ID {user.id} does not have "
        f"{setup['permission'].permission_type} permissions for "
        f"{setup['permission'].resource_type} ID {node.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for Node remove interface endpoint --------------------------------------
# --------------------------------------------------------------------------------------


def test_remove_interface_from_node(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully remove an interface from a node"""

    node = create_random_node(db)
    interface = create_random_form_input_interface(db)
    crud.node.add_interface(db, node=node, interface=interface)
    response = client.post(
        f"{settings.API_V1_STR}/nodes/{node.id}/interfaces/{interface.id}/remove",
        headers=superuser_token_headers,
    )
    db.refresh(node)
    assert response.status_code == 200
    assert interface not in node.interfaces


def test_remove_interface_from_node_fail_node_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the node doesn't exist"""

    interface = create_random_form_input_interface(db)
    response = client.post(
        f"{settings.API_V1_STR}/nodes/{-1}/interfaces/{interface.id}/remove",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find node."


def test_remove_interface_from_node_fail_interface_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the interface doesn't exist"""

    node = create_random_node(db)
    response = client.post(
        f"{settings.API_V1_STR}/nodes/{node.id}/interfaces/{-1}/remove",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find interface."


def test_remove_interface_from_node_normal_user(
    client: TestClient, db: Session
) -> None:
    """Successfully remove an interface from a node as a normal user"""

    setup = node_permission_setup(
        db,
        node_type="test",
        permission_type=PermissionTypeEnum.update,
        permission_enabled=True,
    )
    node = setup["node"]
    user = setup["user"]
    interface = create_random_form_input_interface(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    crud.node.add_interface(db, node=node, interface=interface)

    response = client.post(
        f"{settings.API_V1_STR}/nodes/{node.id}/interfaces/{interface.id}/remove",
        headers=user_token_headers,
    )
    db.refresh(node)
    assert response.status_code == 200
    assert interface not in node.interfaces


def test_remove_interface_from_node_normal_user_fail_no_permission(
    client: TestClient, db: Session
) -> None:
    """Successfully add an interface to a node as a normal user"""

    setup = node_permission_setup(
        db,
        node_type="test",
        permission_type=PermissionTypeEnum.update,
        permission_enabled=False,
    )
    node = setup["node"]
    user = setup["user"]
    interface = create_random_form_input_interface(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    response = client.post(
        f"{settings.API_V1_STR}/nodes/{node.id}/interfaces/{interface.id}/remove",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        f"User ID {user.id} does not have "
        f"{setup['permission'].permission_type} permissions for "
        f"{setup['permission'].resource_type} ID {node.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for Node get node with children endpoint --------------------------------
# --------------------------------------------------------------------------------------


def test_get_node_children(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successfully get a node with children listing"""

    setup = node_children_setup(db)
    node = setup["parent_node"]
    child_node = setup["child_node"]
    user_group = setup["user_group"]
    interface = setup["interface"]
    response = client.get(
        f"{settings.API_V1_STR}/nodes/{node.id}/children",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    for child in content:
        if child["child_type"] == "interface":
            assert child["child_id"] == interface.id
        if child["child_type"] == "node":
            assert child["child_id"] == child_node.id
        if child["child_type"] == "user_group":
            assert child["child_id"] == user_group.id


def test_get_node_with_children_fail_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Fail if the node doesn't exist"""

    response = client.get(
        f"{settings.API_V1_STR}/nodes/{-1}/children",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Cannot find node."


def test_get_node_with_children_normal_user(client: TestClient, db: Session) -> None:
    """Successfully get a node with children listing"""

    setup = node_permission_setup(
        db,
        node_type="test",
        permission_type=PermissionTypeEnum.read,
        permission_enabled=True,
    )
    node = setup["node"]
    user = setup["user"]
    user_group = setup["user_group"]
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    response = client.get(
        f"{settings.API_V1_STR}/nodes/{node.id}/children",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 200
    for child in content:
        if child["child_type"] == "user_group":
            assert child["child_id"] == user_group.id


def test_get_node_with_children_normal_user_fail_no_permission(
    client: TestClient, db: Session
) -> None:
    """Fail if the user doesn't have read permissions on the node"""

    setup = node_permission_setup(
        db,
        node_type="test",
        permission_type=PermissionTypeEnum.read,
        permission_enabled=False,
    )
    node = setup["node"]
    user = setup["user"]
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    response = client.get(
        f"{settings.API_V1_STR}/nodes/{node.id}/children",
        headers=user_token_headers,
    )
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == (
        f"User ID {user.id} does not have "
        f"{setup['permission'].permission_type} permissions for "
        f"{setup['permission'].resource_type} ID {node.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
