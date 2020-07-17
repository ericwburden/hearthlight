from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.tests.utils.network import create_random_network
from app.tests.utils.utils import random_lower_string


def test_create_network(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    data = {"name": random_lower_string()}
    response = client.post(
        f"{settings.API_V1_STR}/networks/", headers=superuser_token_headers, json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert "id" in content
    assert "owner_id" in content


def test_read_network(
    client: TestClient, superuser: User, superuser_token_headers: dict, db: Session
) -> None:
    network = create_random_network(db, creator_id=superuser.id)
    response = client.get(
        f"{settings.API_V1_STR}/networks/{network.id}", headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == network.name
    assert content["id"] == network.id
    assert content["created_by_id"] == superuser.id
