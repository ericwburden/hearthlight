import pytest
import random
from itertools import chain
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import ObjectDeletedError

from app import crud
from app.models.user import User
from app.models.user_group import UserGroupPermissionRel
from app.schemas.user_group import UserGroupCreate, UserGroupUpdate
from app.tests.utils.user import create_random_user
from app.tests.utils.node import create_random_node
from app.tests.utils.permission import create_random_permission
from app.tests.utils.utils import random_lower_string


def test_create_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_create_user_group"
    )
    user_group_in = UserGroupCreate(name=random_lower_string(), node_id=node.id)
    user_group = crud.user_group.create(
        db=db, obj_in=user_group_in, created_by_id=normal_user.id
    )
    assert user_group.created_by_id == normal_user.id


def test_get_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_get_user_group"
    )
    user_group_in = UserGroupCreate(name=random_lower_string(), node_id=node.id)
    user_group = crud.user_group.create(
        db=db, obj_in=user_group_in, created_by_id=normal_user.id
    )
    stored_user_group = crud.user_group.get(db=db, id=user_group.id)
    assert stored_user_group
    assert user_group.id == stored_user_group.id
    assert user_group.name == stored_user_group.name
    assert node.id == stored_user_group.node_id


def test_get_multi_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_get_multi_user_group"
    )
    names = [random_lower_string() for n in range(10)]
    new_user_groups_in = [UserGroupCreate(name=name, node_id=node.id) for name in names]
    new_user_groups = [
        crud.user_group.create(
            db=db, obj_in=user_group_in, created_by_id=normal_user.id
        )
        for user_group_in in new_user_groups_in
    ]
    stored_user_groups = crud.user_group.get_multi(db=db)
    stored_user_group_names = [sn.name for sn in stored_user_groups]
    for n in names:
        assert n in stored_user_group_names


def test_update_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_update_user_group"
    )
    name = random_lower_string()
    user_group_in = UserGroupCreate(name=name, node_id=node.id)
    user_group = crud.user_group.create(
        db=db, obj_in=user_group_in, created_by_id=normal_user.id
    )
    name2 = random_lower_string()
    user_group_update = UserGroupUpdate(name=name2)
    user_group2 = crud.user_group.update(
        db=db, db_obj=user_group, obj_in=user_group_update, updated_by_id=normal_user.id
    )
    assert user_group.id == user_group2.id
    assert user_group.name == user_group2.name
    assert user_group.name == name2
    assert user_group.created_by_id == user_group2.created_by_id


def test_delete_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_delete_user_group"
    )
    name = random_lower_string()
    user_group_in = UserGroupCreate(name=name, node_id=node.id)
    user_group = crud.user_group.create(
        db=db, obj_in=user_group_in, created_by_id=normal_user.id
    )
    user_group2 = crud.user_group.remove(db=db, id=user_group.id)
    user_group3 = crud.user_group.get(db=db, id=user_group.id)
    assert user_group3 is None
    assert user_group2.id == user_group.id
    assert user_group2.name == name
    assert user_group2.created_by_id == normal_user.id


def test_add_user_to_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_add_user_to_user_group"
    )
    name = random_lower_string()
    user_group_in = UserGroupCreate(name=name, node_id=node.id)
    user_group = crud.user_group.create(
        db=db, obj_in=user_group_in, created_by_id=normal_user.id
    )
    user = create_random_user(db)

    association = crud.user_group.add_user_to_group(
        db=db, user_group=user_group, user_id=user.id
    )
    assert association.user_group_id == user_group.id
    assert association.user_id == user.id


def test_get_user_group_users(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_get_user_group_users"
    )
    name = random_lower_string()
    user_group_in = UserGroupCreate(name=name, node_id=node.id)
    user_group = crud.user_group.create(
        db=db, obj_in=user_group_in, created_by_id=normal_user.id
    )

    user1 = create_random_user(db)
    user2 = create_random_user(db)
    user3 = create_random_user(db)
    crud.user_group.add_user_to_group(db=db, user_group=user_group, user_id=user1.id)
    crud.user_group.add_user_to_group(db=db, user_group=user_group, user_id=user2.id)
    group_users = crud.user_group.get_users(db, user_group=user_group)

    for user in group_users:
        assert user.id in [user1.id, user2.id]
        assert user.id != user3.id


def test_remove_user_from_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_remove_user_from_user_group"
    )
    name = random_lower_string()
    user_group_in = UserGroupCreate(name=name, node_id=node.id)
    user_group = crud.user_group.create(
        db=db, obj_in=user_group_in, created_by_id=normal_user.id
    )

    user = create_random_user(db)
    association = crud.user_group.add_user_to_group(
        db=db, user_group=user_group, user_id=user.id
    )
    crud.user_group.remove_user_from_group(db=db, user_group=user_group, user=user)
    group_users = crud.user_group.get_users(db, user_group=user_group)

    with pytest.raises(ObjectDeletedError):
        assert association.user_group_id

    for group_user in group_users:
        assert group_user.id != user.id


def test_add_permission_to_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_add_permission_to_user_group"
    )
    name = random_lower_string()
    user_group_in = UserGroupCreate(name=name, node_id=node.id)
    user_group = crud.user_group.create(
        db=db, obj_in=user_group_in, created_by_id=normal_user.id
    )
    permission = create_random_permission(db, node_id=node.id)

    association = crud.user_group.add_permission(
        db=db, user_group=user_group, permission=permission, enabled=True
    )
    assert association.user_group_id == user_group.id
    assert association.permission_id == permission.id
    assert association.enabled == True


def test_get_permission_for_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_get_permission_for_user_group"
    )
    name = random_lower_string()
    user_group_in = UserGroupCreate(name=name, node_id=node.id)
    user_group = crud.user_group.create(
        db=db, obj_in=user_group_in, created_by_id=normal_user.id
    )
    permission = create_random_permission(db, node_id=node.id)
    crud.user_group.add_permission(
        db=db, user_group=user_group, permission=permission, enabled=True
    )
    stored_permission = crud.user_group.get_permission(
        db=db, user_group=user_group, permission_id=permission.id
    )

    assert permission.id == stored_permission.id
    assert permission.resource_id == stored_permission.resource_id
    assert permission.permission_type == stored_permission.permission_type


def test_get_all_permissions_for_user_group(db: Session, normal_user: User) -> None:
    nodes = [
        create_random_node(
            db,
            created_by_id=normal_user.id,
            node_type="test_get_all_permissions_for_user_group",
        )
        for n in range(10)
    ]
    name = random_lower_string()
    user_group_in = UserGroupCreate(name=name, node_id=random.choice(nodes).id)
    user_group = crud.user_group.create(
        db=db, obj_in=user_group_in, created_by_id=normal_user.id
    )
    permissions = chain(
        *[crud.node.instantiate_permissions(db, node=node) for node in nodes]
    )
    for permission in permissions:
        crud.user_group.add_permission(
            db=db, user_group=user_group, permission=permission, enabled=True
        )
    stored_permissions = crud.user_group.get_all_permissions(
        db=db, user_group=user_group
    )

    for permission in permissions:
        assert permission.id in [sp.id for sp in stored_permissions]
        assert permission.resource_id in [sp.resource_id for sp in stored_permissions]
        assert permission.permission_type in [
            sp.permission_type for sp in stored_permissions
        ]


def test_delete_permission_from_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db,
        created_by_id=normal_user.id,
        node_type="test_delete_permission_from_user_group",
    )
    name = random_lower_string()
    user_group_in = UserGroupCreate(name=name, node_id=node.id)
    user_group = crud.user_group.create(
        db=db, obj_in=user_group_in, created_by_id=normal_user.id
    )
    permission = create_random_permission(db, node_id=node.id)

    association = crud.user_group.add_permission(
        db=db, user_group=user_group, permission=permission, enabled=True
    )
    deleted_user_group_permission = crud.user_group.delete_permission(
        db=db, user_group=user_group, permission=permission
    )
    stored_permission = crud.user_group.get_permission(
        db, user_group=user_group, permission_id=permission.id
    )

    assert deleted_user_group_permission.permission_id == permission.id
    assert stored_permission is None


def test_grant_permission_to_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db,
        created_by_id=normal_user.id,
        node_type="test_grant_permission_to_user_group",
    )
    name = random_lower_string()
    user_group_in = UserGroupCreate(name=name, node_id=node.id)
    user_group = crud.user_group.create(
        db=db, obj_in=user_group_in, created_by_id=normal_user.id
    )
    permission = create_random_permission(db, node_id=node.id)
    crud.user_group.add_permission(
        db=db, user_group=user_group, permission=permission, enabled=False
    )

    association = crud.user_group.grant_permission(
        db=db, user_group=user_group, permission=permission
    )
    assert association.user_group_id == user_group.id
    assert association.permission_id == permission.id
    assert association.enabled == True


def test_revoke_permission_for_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db,
        created_by_id=normal_user.id,
        node_type="test_revoke_permission_for_user_group",
    )
    name = random_lower_string()
    user_group_in = UserGroupCreate(name=name, node_id=node.id)
    user_group = crud.user_group.create(
        db=db, obj_in=user_group_in, created_by_id=normal_user.id
    )
    permission = create_random_permission(db, node_id=node.id)
    crud.user_group.add_permission(
        db=db, user_group=user_group, permission=permission, enabled=True
    )

    association = crud.user_group.revoke_permission(
        db=db, user_group=user_group, permission=permission
    )
    assert association.user_group_id == user_group.id
    assert association.permission_id == permission.id
    assert association.enabled == False
