from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import random_lower_string
from app.tests.utils.node import create_random_node

# --------------------------------------------------------------------------------------
# region Tests for Node create endpoint ------------------------------------------------
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
