import random
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud
from app.core.security import verify_password
from app.models.user import User
from app.schemas.permission import (
    PermissionTypeEnum,
    PermissionCreate,
    ResourceTypeEnum,
)
from app.schemas.user import UserCreate, UserUpdate
from app.tests.utils.node import create_random_node
from app.tests.utils.permission import create_random_permission
from app.tests.utils.user_group import create_random_user_group
from app.tests.utils.utils import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.user.create(db, obj_in=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.user.create(db, obj_in=user_in)
    authenticated_user = crud.user.authenticate(db, email=email, password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = crud.user.authenticate(db, email=email, password=password)
    assert user is None


def test_check_if_user_is_active(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.user.create(db, obj_in=user_in)
    is_active = crud.user.is_active(user)
    assert is_active is True


def test_check_if_user_is_active_inactive(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, disabled=True)
    user = crud.user.create(db, obj_in=user_in)
    is_active = crud.user.is_active(user)
    assert is_active


def test_check_if_user_is_superuser(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = crud.user.create(db, obj_in=user_in)
    is_superuser = crud.user.is_superuser(user)
    assert is_superuser is True


def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.user.create(db, obj_in=user_in)
    is_superuser = crud.user.is_superuser(user)
    assert is_superuser is False


def test_get_user(db: Session) -> None:
    password = random_lower_string()
    username = random_email()
    user_in = UserCreate(email=username, password=password, is_superuser=True)
    user = crud.user.create(db, obj_in=user_in)
    user_2 = crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(db: Session) -> None:
    password = random_lower_string()
    email = random_email()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = crud.user.create(db, obj_in=user_in)
    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    crud.user.update(db, db_obj=user, obj_in=user_in_update)
    user_2 = crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)


def test_get_user_groups_for_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.user.create(db, obj_in=user_in)

    user_group1 = create_random_user_group(db, created_by_id=user.id)
    user_group2 = create_random_user_group(db, created_by_id=user.id)
    user_group3 = create_random_user_group(db, created_by_id=user.id)

    crud.user_group.add_user_to_group(db, user_group=user_group1, user=user)
    crud.user_group.add_user_to_group(db, user_group=user_group2, user=user)

    user_user_groups = crud.user.get_user_groups(db, user=user)

    for user_group in user_user_groups:
        assert user_group.id in [user_group1.id, user_group2.id]
        assert user_group.id != user_group3.id


def test_verify_user_node_permission(db: Session, normal_user: User) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.user.create(db, obj_in=user_in)
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="verify_user_node_permission"
    )
    user_group = create_random_user_group(db, created_by_id=normal_user.id)
    crud.user_group.add_user_to_group(db, user_group=user_group, user=user)

    permission = create_random_permission(db, node_id=node.id)
    crud.user_group.add_permission(
        db, user_group=user_group, permission=permission, enabled=True
    )
    has_permission = crud.user.has_permission(
        db,
        user=user,
        resource_type="node",
        resource_id=node.id,
        permission_type=permission.permission_type,
    )

    # Need to add an explicit 'False' permission for the User to the resource
    # to ensure that will return False in addition to the missing permissions
    permissions_not_granted = [
        i for i in list(PermissionTypeEnum) if i != permission.permission_type
    ]
    permission_type = random.choice(permissions_not_granted)
    permission_in = PermissionCreate(
        resource_id=node.id,
        resource_type=ResourceTypeEnum.node,
        permission_type=permission_type,
        enabled=False,
    )
    permission_not_granted = crud.node_permission.create(db=db, obj_in=permission_in)

    assert has_permission == True
    for png in permissions_not_granted:
        has_permission = crud.user.has_permission(
            db,
            user=user,
            resource_type="node",
            resource_id=node.id,
            permission_type=png,
        )
        assert has_permission == False
