import random
from sqlalchemy.orm import Session

from app import crud
from app.models.user import User
from app.schemas.permission import (
    PermissionCreate,
    PermissionTypeEnum,
    ResourceTypeEnum,
)
from app.tests.utils.node import create_random_node
from app.tests.utils.user_group import create_random_user_group

# --------------------------------------------------------------------------------------
# region | Tests for basic CRUD functions ----------------------------------------------
# --------------------------------------------------------------------------------------


def test_create_node_permission(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_create_permission"
    )
    permission_type = random.choice(list(PermissionTypeEnum))
    permission_in = PermissionCreate(
        resource_id=node.id,
        resource_type=ResourceTypeEnum.node,
        permission_type=permission_type,
    )
    permission = crud.node_permission.create(db=db, obj_in=permission_in)

    assert permission.resource_id == node.id
    assert permission.permission_type == permission_type


def test_get_node_permission(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_get_permission"
    )
    permission_type = random.choice(list(PermissionTypeEnum))
    permission_in = PermissionCreate(
        resource_id=node.id,
        resource_type=ResourceTypeEnum.node,
        permission_type=permission_type,
    )
    permission = crud.node_permission.create(db=db, obj_in=permission_in)
    stored_permission = crud.node_permission.get(db=db, id=permission.id)

    assert stored_permission
    assert permission.id == stored_permission.id
    assert permission.resource_id == stored_permission.resource_id
    assert permission.permission_type == stored_permission.permission_type


def test_get_multi_node_permission(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_get_multi_permission"
    )
    permission_types = list(PermissionTypeEnum)
    new_permissions_in = [
        PermissionCreate(
            resource_id=node.id, resource_type=ResourceTypeEnum.node, permission_type=pt
        )
        for pt in permission_types
    ]
    [
        crud.node_permission.create(db=db, obj_in=permission_in)
        for permission_in in new_permissions_in
    ]
    stored_permissions = crud.node_permission.get_multi(db=db)
    stored_permission_permission_types = [
        sp.permission_type for sp in stored_permissions
    ]

    for pt in permission_types:
        assert pt in stored_permission_permission_types


def test_delete_node_permission(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_delete_permission"
    )
    permission_type = random.choice(list(PermissionTypeEnum))
    permission_in = PermissionCreate(
        resource_id=node.id,
        resource_type=ResourceTypeEnum.node,
        permission_type=permission_type,
    )
    permission = crud.node_permission.create(db=db, obj_in=permission_in)
    permission2 = crud.node_permission.remove(db=db, id=permission.id)
    permission3 = crud.node_permission.get(db=db, id=permission.id)

    assert permission3 is None
    assert permission2.id == permission.id
    assert permission2.resource_id == node.id

# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for granting permissions to a user group ------------------------------
# --------------------------------------------------------------------------------------

def test_grant_single_permission(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_grant_single_permission"
    )
    user_group = create_random_user_group(
        db, created_by_id=normal_user.id, node_id=node.id
    )
    permission = crud.node.get_permission(
        db, id=node.id, permission_type=PermissionTypeEnum.read
    )
    user_group_permission_rel = crud.permission.grant(
        db,  user_group_id=user_group.id, permission_id=permission.id
    )
    assert user_group_permission_rel.user_group_id == user_group.id
    assert user_group_permission_rel.permission_id == permission.id
    assert user_group_permission_rel.enabled

def test_grant_single_permission_existing(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_grant_single_permission"
    )
    user_group = create_random_user_group(
        db, created_by_id=normal_user.id, node_id=node.id
    )
    permission = crud.node.get_permission(
        db, id=node.id, permission_type=PermissionTypeEnum.read
    )
    # Grant then revoke the permission before trying to grant it again
    crud.permission.grant(db, user_group_id=user_group.id, permission_id=permission.id)
    crud.permission.revoke(db, user_group_id=user_group.id, permission_id=permission.id)
    user_group_permission_rel = crud.permission.grant(
        db,  user_group_id=user_group.id, permission_id=permission.id
    )
    assert user_group_permission_rel.user_group_id == user_group.id
    assert user_group_permission_rel.permission_id == permission.id
    assert user_group_permission_rel.enabled

def test_grant_multiple_permissions(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_grant_multiple_permissions"
    )
    user_group = create_random_user_group(
        db, created_by_id=normal_user.id, node_id=node.id
    )
    permissions = crud.node.get_permissions(db, id=node.id)
    permission_ids = [p.id for p in permissions]
    user_group_permission_rels = crud.permission.grant_multiple(
        db,  user_group_id=user_group.id, permission_ids=permission_ids
    )
    assert len(permission_ids) == len(user_group_permission_rels)
    for ugpr in user_group_permission_rels:
        assert ugpr.user_group_id == user_group.id
        assert ugpr.enabled

def test_grant_multiple_permissions_existing(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_grant_multiple_permissions"
    )
    user_group = create_random_user_group(
        db, created_by_id=normal_user.id, node_id=node.id
    )
    permissions = crud.node.get_permissions(db, id=node.id)
    permission_ids = [p.id for p in permissions]
    # Grant then revoke the permissions before trying to grant them again
    crud.permission.grant_multiple(
        db,  user_group_id=user_group.id, permission_ids=permission_ids
    )
    crud.permission.revoke_multiple(
        db,  user_group_id=user_group.id, permission_ids=permission_ids[:2]
    )
    user_group_permission_rels = crud.permission.grant_multiple(
        db,  user_group_id=user_group.id, permission_ids=permission_ids
    )
    assert len(permission_ids) == len(user_group_permission_rels)
    for ugpr in user_group_permission_rels:
        assert ugpr.user_group_id == user_group.id
        assert ugpr.enabled
