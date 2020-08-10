from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas import PermissionTypeEnum
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.node import create_random_node
from app.tests.utils.utils import random_lower_string
from app.tests.utils.setup import node_permission_setup


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for Node create user group endpoint -------------------------------------
# --------------------------------------------------------------------------------------


def test_create_user_group(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    """Successful user_group creation"""
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
    """Successfully create user group with normal user"""

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


def test_create_user_group_fail_no_permission(client: TestClient, db: Session) -> None:
    """User Group creation fails without create permission on the node"""

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
