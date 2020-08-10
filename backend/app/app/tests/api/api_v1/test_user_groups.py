from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.node import create_random_node
from app.tests.utils.utils import random_lower_string


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
