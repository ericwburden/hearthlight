from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.schemas.user import UserCreate
from app.schemas.permission import PermissionTypeEnum
from app.tests.utils.user import create_random_user, authentication_token_from_email
from app.tests.utils.user_group import create_random_user_group
from app.tests.utils.utils import random_email, random_lower_string


# --------------------------------------------------------------------------------------
# region | Tests for User create user endpoint -----------------------------------------
# --------------------------------------------------------------------------------------


def test_create_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    data = {"email": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    user = crud.user.get_by_email(db, email=username)
    assert 200 <= r.status_code < 300
    assert user
    assert user.email == created_user["email"]


def test_create_user_normal_user(client: TestClient, db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user_group = create_random_user_group(db)
    data = {"email": username, "password": password, "user_group_id": user_group.id}

    user = create_random_user(db)
    crud.user_group.add_user(db, user_group=user_group, user_id=user.id)
    create_permission = crud.user_group.get_permission(
        db, id=user_group.id, permission_type=PermissionTypeEnum.create
    )
    crud.permission.grant(
        db, user_group_id=user_group.id, permission_id=create_permission.id
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=user_token_headers,
        json=data,
    )
    created_user = r.json()
    user = crud.user.get_by_email(db, email=username)
    assert 200 <= r.status_code < 300
    assert user
    assert user.email == created_user["email"]
    assert user_group in user.user_groups


def test_create_user_fail_user_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    user = create_random_user(db)
    data = {"email": user.email, "password": user.hashed_password}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    content = r.json()
    assert r.status_code == 400
    assert (
        content["detail"] == "The user with this username already exists in the system."
    )


def test_create_user_fail_user_group_not_exists(
    client: TestClient, db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    data = {"email": username, "password": password, "user_group_id": -1}
    user = create_random_user(db)
    user_group = create_random_user_group(db)
    crud.user_group.add_user(db, user_group=user_group, user_id=user.id)
    create_permission = crud.user_group.get_permission(
        db, id=user_group.id, permission_type=PermissionTypeEnum.create
    )
    crud.permission.grant(
        db, user_group_id=user_group.id, permission_id=create_permission.id
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=user_token_headers,
        json=data,
    )
    content = r.json()
    user = crud.user.get_by_email(db, email=username)
    assert r.status_code == 404
    assert user is None
    assert content["detail"] == "Can not find user group."


def test_create_user_fail_normal_user_no_user_group(
    client: TestClient, db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user_group = create_random_user_group(db)
    data = {"email": username, "password": password}

    user = create_random_user(db)
    crud.user_group.add_user(db, user_group=user_group, user_id=user.id)
    create_permission = crud.user_group.get_permission(
        db, id=user_group.id, permission_type=PermissionTypeEnum.create
    )
    crud.permission.grant(
        db, user_group_id=user_group.id, permission_id=create_permission.id
    )
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=user_token_headers,
        json=data,
    )
    content = r.json()
    user = crud.user.get_by_email(db, email=username)
    assert r.status_code == 403
    assert user is None
    assert content["detail"] == "Non-superuser must provide a user group."


def test_create_user_fail_normal_user_no_permission(
    client: TestClient, db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user_group = create_random_user_group(db)
    data = {"email": username, "password": password, "user_group_id": user_group.id}

    user = create_random_user(db)
    crud.user_group.add_user(db, user_group=user_group, user_id=user.id)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=user_token_headers,
        json=data,
    )
    content = r.json()
    returned_user = crud.user.get_by_email(db, email=username)
    assert r.status_code == 403
    assert returned_user is None
    assert content["detail"] == (
        f"User ID {user.id} does not have create permissions for "
        f"user_group ID {user_group.id}"
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for User read one user endpoint ---------------------------------------
# --------------------------------------------------------------------------------------


def test_get_existing_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.user.create(db, obj_in=user_in)
    user_id = user.id
    r = client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = crud.user.get_by_email(db, email=username)
    assert existing_user
    assert existing_user.email == api_user["email"]


def test_get_users_superuser_me(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"]
    assert current_user["email"] == settings.FIRST_SUPERUSER


def test_get_users_normal_user_me(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user["email"] == settings.EMAIL_TEST_USER


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for User read multiple users endpoint ---------------------------------
# --------------------------------------------------------------------------------------


def test_retrieve_users(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    crud.user.create(db, obj_in=user_in)

    username2 = random_email()
    password2 = random_lower_string()
    user_in2 = UserCreate(email=username2, password=password2)
    crud.user.create(db, obj_in=user_in2)

    r = client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
    all_users = r.json()["records"]

    assert len(all_users) > 1
    for item in all_users:
        assert "email" in item


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for User update user endpoint -----------------------------------------
# --------------------------------------------------------------------------------------


def test_update_user_me_normal_user(client: TestClient, db: Session) -> None:
    user = create_random_user(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    data = {"email": random_email()}
    r = client.put(
        f"{settings.API_V1_STR}/users/me", headers=user_token_headers, json=data
    )
    content = r.json()
    assert r.status_code == 200
    assert content["email"] == data["email"]


def test_update_user_me_normal_user_fail_email_exists(
    client: TestClient, db: Session
) -> None:
    user = create_random_user(db)
    another_user = create_random_user(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    data = {"email": another_user.email}
    r = client.put(
        f"{settings.API_V1_STR}/users/me", headers=user_token_headers, json=data
    )
    content = r.json()
    assert r.status_code == 400
    assert (
        content["detail"] == "A user with this username already exists in the system."
    )


def test_update_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    user = create_random_user(db)
    data = {"email": random_email()}
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    content = r.json()
    assert r.status_code == 200
    assert content["email"] == data["email"]


def test_update_user_fail_user_not_exist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    data = {"email": random_email()}
    r = client.put(
        f"{settings.API_V1_STR}/users/{-1}", headers=superuser_token_headers, json=data
    )
    content = r.json()
    assert r.status_code == 404
    assert content["detail"] == "Can not find user."


def test_update_user_fail_normal_user(client: TestClient, db: Session) -> None:
    user = create_random_user(db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    data = {"email": random_email()}
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}", headers=user_token_headers, json=data
    )
    content = r.json()
    assert r.status_code == 400
    assert content["detail"] == "The user is not a superuser"


def test_update_user_fail_email_exists(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    user = create_random_user(db)
    another_user = create_random_user(db)
    data = {"email": another_user.email}
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    content = r.json()
    assert r.status_code == 400
    assert (
        content["detail"] == "A user with this username already exists in the system."
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
