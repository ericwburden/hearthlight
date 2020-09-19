from typing import Dict, Union, List

from sqlalchemy.orm import Session

from app import crud, models
from app.schemas import PermissionTypeEnum
from app.tests.utils.node import create_random_node
from app.tests.utils.user import create_random_user
from app.tests.utils.user_group import create_random_user_group
from app.tests.utils.query import create_random_query_interface


def node_permission_setup(
    db: Session,
    *,
    node_type: str,
    permission_type: PermissionTypeEnum,
    permission_enabled: bool
) -> Dict[str, Union[models.Node, models.Permission, models.UserGroup, models.User]]:
    """
    Setup: Create the node, get create permission, create user, create
    user group, add user to user group, give user group specified
    permission on the node

    Returns a dictionary of the format: {
        "node": Node,
        "permission": Permission,
        "user_group": UserGroup,
        "user": User,
    }
    """

    node = create_random_node(db, created_by_id=1, node_type=node_type)
    permission = crud.node.get_permission(
        db, id=node.id, permission_type=permission_type
    )
    user = create_random_user(db)
    user_group = create_random_user_group(db, created_by_id=1, node_id=node.id)
    crud.user_group.add_user(db, user_group=user_group, user_id=user.id)
    crud.permission.grant(db, user_group_id=user_group.id, permission_id=permission.id)
    if not permission_enabled:
        crud.permission.revoke(
            db, user_group_id=user_group.id, permission_id=permission.id
        )
    return {
        "node": node,
        "permission": permission,
        "user_group": user_group,
        "user": user,
    }


def node_all_permissions_setup(
    db: Session,
) -> Dict[str, Union[models.Node, models.Permission, models.UserGroup, models.User]]:
    """
    Setup: Create the node, get all node permissions, create the user,
    create the user group, add the user to the user group, grant all
    the permissions to the user group

    Returns a dictionary of the format: {
        "node": Node,
        "permissions": List[Permission],
        "user_group": UserGroup,
        "user": User,
    }
    """

    node = create_random_node(
        db, created_by_id=1, node_type="node_all_permissions_setup"
    )
    permissions = crud.node.get_permissions(db, id=node.id)
    user = create_random_user(db)
    user_group = create_random_user_group(db, created_by_id=1, node_id=node.id)
    crud.user_group.add_user(db, user_group=user_group, user_id=user.id)
    crud.permission.grant_multiple(
        db, user_group_id=user_group.id, permission_ids=[p.id for p in permissions]
    )
    return {
        "node": node,
        "permissions": permissions,
        "user_group": user_group,
        "user": user,
    }


def multi_node_permission_setup(
    db: Session,
    *,
    n: int,
    node_type: str,
    permission_type: PermissionTypeEnum,
    permission_enabled: bool
) -> Dict[
    str,
    Union[List[models.Node], List[models.Permission], models.UserGroup, models.User],
]:
    """
    Setup: Create 'n' nodes, get create permissions, create user, create
    user group, add user to user group, give user group specified
    permission on all nodes

    Returns a dictionary of the format: {
        "nodes": [Node],
        "permissions": [Permission],
        "user_group": UserGroup,
        "user": User,
    }
    """

    nodes = [
        create_random_node(db, created_by_id=1, node_type=node_type) for i in range(n)
    ]
    user = create_random_user(db)
    user_group = create_random_user_group(db, created_by_id=1, node_id=nodes[0].id)
    crud.user_group.add_user(db, user_group=user_group, user_id=user.id)
    permissions = []
    for node in nodes:
        permission = crud.node.get_permission(
            db, id=node.id, permission_type=permission_type
        )
        permissions.append(permission)
        crud.permission.grant(
            db, user_group_id=user_group.id, permission_id=permission.id
        )
        if not permission_enabled:
            crud.permission.revoke(
                db, user_group_id=user_group.id, permission_id=permission.id
            )
    return {
        "nodes": nodes,
        "permissions": permissions,
        "user_group": user_group,
        "user": user,
    }


def user_group_permission_setup(
    db: Session, *, permission_type: PermissionTypeEnum, permission_enabled: bool
) -> Dict[str, Union[models.Node, models.Permission, models.UserGroup, models.User]]:
    """
    Setup: Create a node, create a user, create a user group, get the
    specified permission, add the user to the user group, grant the
    user group the specified permission (to itself)

    Returns a dictionary of the format: {
        "node": Node,
        "permission": Permission,
        "user_group": UserGroup,
        "user": User,
    }
    """

    node = create_random_node(
        db, created_by_id=1, node_type="user_group_permission_setup"
    )
    user = create_random_user(db)
    user_group = create_random_user_group(db, created_by_id=1, node_id=node.id)
    permission = crud.user_group.get_permission(
        db, id=user_group.id, permission_type=permission_type
    )
    crud.user_group.add_user(db, user_group=user_group, user_id=user.id)
    crud.permission.grant(db, user_group_id=user_group.id, permission_id=permission.id)
    if not permission_enabled:
        crud.permission.revoke(
            db, user_group_id=user_group.id, permission_id=permission.id
        )
    return {
        "node": node,
        "permission": permission,
        "user_group": user_group,
        "user": user,
    }


def multi_user_group_permission_setup(
    db: Session,
    *,
    n: int,
    permission_type: PermissionTypeEnum,
    permission_enabled: bool
) -> Dict[
    str,
    Union[models.Node, List[models.Permission], List[models.UserGroup], models.User],
]:
    """
    Setup: Create a parent node, create a user, create 'n' user groups,
    add user to all groups, give each user group the specified
    permission.

    Returns a dictionary of the format: {
        "node": Node,
        "permissions": [Permission],
        "user_groups": [UserGroup],
        "user": User,
    }
    """

    node = create_random_node(
        db, created_by_id=1, node_type="multi_user_group_permission_setup"
    )
    user = create_random_user(db)
    user_groups = [
        create_random_user_group(db, created_by_id=1, node_id=node.id) for i in range(n)
    ]
    permissions = []
    for user_group in user_groups:
        permission = crud.user_group.get_permission(
            db, id=user_group.id, permission_type=permission_type
        )
        permissions.append(permission)
        crud.user_group.add_user(db, user_group=user_group, user_id=user.id)
        crud.permission.grant(
            db, user_group_id=user_group.id, permission_id=permission.id
        )
        if not permission_enabled:
            crud.permission.revoke(
                db, user_group_id=user_group.id, permission_id=permission.id
            )
    return {
        "node": node,
        "permissions": permissions,
        "user_groups": user_groups,
        "user": user,
    }


def form_input_permission_setup(
    db: Session, *, permission_type: PermissionTypeEnum, permission_enabled: bool = True
) -> Dict[
    str, Union[models.Interface, models.Permission, models.UserGroup, models.User]
]:
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    user = create_random_user(db)
    user_group = create_random_user_group(db)
    permission = crud.form_input.get_permission(
        db, id=form_input.id, permission_type=permission_type
    )
    crud.user_group.add_user(db, user_group=user_group, user_id=user.id)
    crud.permission.grant(db, user_group_id=user_group.id, permission_id=permission.id)
    if not permission_enabled:
        crud.permission.revoke(
            db, user_group_id=user_group.id, permission_id=permission.id
        )
    return {
        "form_input": form_input,
        "permission": permission,
        "user_group": user_group,
        "user": user,
    }


def query_permission_setup(
    db: Session, *, permission_type: PermissionTypeEnum, permission_enabled: bool = True
) -> Dict[
    str, Union[models.QueryInterface, models.Permission, models.UserGroup, models.User]
]:
    query = create_random_query_interface(db)
    user = create_random_user(db)
    user_group = create_random_user_group(db)
    permission = crud.query.get_permission(
        db, id=query.id, permission_type=permission_type
    )
    crud.user_group.add_user(db, user_group=user_group, user_id=user.id)
    crud.permission.grant(db, user_group_id=user_group.id, permission_id=permission.id)
    if not permission_enabled:
        crud.permission.revoke(
            db, user_group_id=user_group.id, permission_id=permission.id
        )
    return {
        "query": query,
        "permission": permission,
        "user_group": user_group,
        "user": user,
    }
