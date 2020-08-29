import pytest
import random
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from app import crud
from app.crud.errors import MissingRecordsError
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
        db, user_group_id=user_group.id, permission_id=permission.id
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
        db, user_group_id=user_group.id, permission_id=permission.id
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
        db, user_group_id=user_group.id, permission_ids=permission_ids
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
        db, user_group_id=user_group.id, permission_ids=permission_ids
    )
    crud.permission.revoke_multiple(
        db, user_group_id=user_group.id, permission_ids=permission_ids[:2]
    )
    user_group_permission_rels = crud.permission.grant_multiple(
        db, user_group_id=user_group.id, permission_ids=permission_ids
    )
    assert len(permission_ids) == len(user_group_permission_rels)
    for ugpr in user_group_permission_rels:
        assert ugpr.user_group_id == user_group.id
        assert ugpr.enabled


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for revoking permissions in a user group ------------------------------
# --------------------------------------------------------------------------------------


def test_revoke_single_permission(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_revoke_single_permission"
    )
    user_group = create_random_user_group(
        db, created_by_id=normal_user.id, node_id=node.id
    )
    permission = crud.node.get_permission(
        db, id=node.id, permission_type=PermissionTypeEnum.read
    )
    crud.permission.grant(db, user_group_id=user_group.id, permission_id=permission.id)
    user_group_permission_rel = crud.permission.revoke(
        db, user_group_id=user_group.id, permission_id=permission.id
    )
    assert user_group_permission_rel.user_group_id == user_group.id
    assert user_group_permission_rel.permission_id == permission.id
    assert not user_group_permission_rel.enabled


def test_revoke_single_permission_missing(db: Session, normal_user: User) -> None:
    """
    Raises a NoResultFound error if the user_group/permission
    relationship doesn't exist
    """
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_revoke_single_permission"
    )
    user_group = create_random_user_group(
        db, created_by_id=normal_user.id, node_id=node.id
    )
    permission = crud.node.get_permission(
        db, id=node.id, permission_type=PermissionTypeEnum.read
    )
    with pytest.raises(NoResultFound):
        crud.permission.revoke(
            db, user_group_id=user_group.id, permission_id=permission.id
        )


def test_revoke_multiple_permissions(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_revoke_multiple_permissions"
    )
    user_group = create_random_user_group(
        db, created_by_id=normal_user.id, node_id=node.id
    )
    permissions = crud.node.get_permissions(db, id=node.id)
    permission_ids = [p.id for p in permissions]
    crud.permission.grant_multiple(
        db, user_group_id=user_group.id, permission_ids=permission_ids
    )
    user_group_permission_rels = crud.permission.revoke_multiple(
        db, user_group_id=user_group.id, permission_ids=permission_ids
    )
    assert len(permission_ids) == len(user_group_permission_rels)
    for ugpr in user_group_permission_rels:
        assert ugpr.user_group_id == user_group.id
        assert not ugpr.enabled


def test_revoke_multiple_permissions_missing(db: Session, normal_user: User) -> None:
    """
    Raises a MissingRecordsError if one or more permissions are a not
    associated with the user group, making them ineligible to be revoked
    """
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_revoke_multiple_permissions"
    )
    user_group = create_random_user_group(
        db, created_by_id=normal_user.id, node_id=node.id
    )
    permissions = crud.node.get_permissions(db, id=node.id)
    permission_ids = [p.id for p in permissions]
    with pytest.raises(MissingRecordsError):
        crud.permission.revoke_multiple(
            db, user_group_id=user_group.id, permission_ids=permission_ids
        )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests for confirming permission location in relation to nodes ---------------
# --------------------------------------------------------------------------------------


def test_all_in_database_check(db: Session, normal_user: User) -> None:
    node = create_random_node(
        db, created_by_id=normal_user.id, node_type="test_all_in_database_check"
    )
    permissions = crud.node.get_permissions(db, id=node.id)
    all_permission_ids = [p.id for p in permissions]
    no_permission_ids = [-1, -100]
    some_permission_ids = [*no_permission_ids, *all_permission_ids]

    all_permissions_check = crud.permission.all_in_database(
        db, permission_ids=all_permission_ids
    )
    no_permission_check = crud.permission.all_in_database(
        db, permission_ids=no_permission_ids
    )
    some_permission_check = crud.permission.all_in_database(
        db, permission_ids=some_permission_ids
    )

    assert all_permissions_check
    assert not no_permission_check
    assert not some_permission_check


def test_in_node_descendants_check(db: Session, normal_user: User) -> None:
    node = create_random_node(db, created_by_id=normal_user.id, node_type="parent")
    node_create_permission = crud.node.get_permission(
        db, id=node.id, permission_type=PermissionTypeEnum.create
    )
    node2 = create_random_node(
        db, created_by_id=normal_user.id, node_type="child", parent_id=node.id
    )
    node2_read_permission = crud.node.get_permission(
        db, id=node2.id, permission_type=PermissionTypeEnum.read
    )
    node3 = create_random_node(
        db, created_by_id=normal_user.id, node_type="child", parent_id=node2.id
    )
    node3_update_permission = crud.node.get_permission(
        db, id=node3.id, permission_type=PermissionTypeEnum.update
    )

    pass1 = crud.permission.in_node_descendants(
        db, node_id=node.id, permission=node_create_permission
    )
    pass2 = crud.permission.in_node_descendants(
        db, node_id=node.id, permission=node2_read_permission
    )
    pass3 = crud.permission.in_node_descendants(
        db, node_id=node2.id, permission=node3_update_permission
    )
    fail = crud.permission.in_node_descendants(
        db, node_id=node3.id, permission=node_create_permission
    )

    assert pass1
    assert pass2
    assert pass3
    assert not fail


def test_all_node_descendants(db: Session, normal_user: User) -> None:
    node = create_random_node(db, created_by_id=normal_user.id, node_type="parent")
    child_node = create_random_node(
        db, created_by_id=normal_user.id, node_type="child", parent_id=node.id
    )
    user_group1 = create_random_user_group(
        db, created_by_id=normal_user.id, node_id=node.id
    )
    user_group2 = create_random_user_group(
        db, created_by_id=normal_user.id, node_id=child_node.id
    )
    not_child_node = create_random_node(
        db, created_by_id=normal_user.id, node_type="not_child"
    )

    child_node_permissions = crud.node.get_permissions(db, id=child_node.id)
    user_group1_permissions = crud.user_group.get_permissions(db, id=user_group1.id)
    user_group2_permissions = crud.user_group.get_permissions(db, id=user_group2.id)
    not_child_node_permissions = crud.node.get_permissions(db, id=not_child_node.id)

    all_permissions = [
        *child_node_permissions,
        *user_group1_permissions,
        *user_group2_permissions,
    ]
    some_permissions = [*child_node_permissions, *not_child_node_permissions]
    no_permissions = [*not_child_node_permissions]

    pass1 = crud.permission.all_node_descendants(
        db, node_id=node.id, permissions=all_permissions
    )
    fail1 = crud.permission.all_node_descendants(
        db, node_id=node.id, permissions=some_permissions
    )
    fail2 = crud.permission.all_node_descendants(
        db, node_id=node.id, permissions=no_permissions
    )

    assert pass1
    assert not fail1
    assert not fail2


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
