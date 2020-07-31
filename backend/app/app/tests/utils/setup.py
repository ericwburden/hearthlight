
from typing import Dict, Union

from sqlalchemy.orm import Session

from app import crud, models
from app.schemas import PermissionTypeEnum  
from app.tests.utils.node import create_random_node
from app.tests.utils.user import create_random_user
from app.tests.utils.user_group import create_random_user_group

def node_permission_setup(
    db: Session,
    *,
    node_type: str,
    permission_type: PermissionTypeEnum,
    permission_enabled: bool
) -> Dict[str, Union[models.Node, models.Permission, models.UserGroup, models.User]]:
    """
    Setup: Create the parent node, instantiate permissions, get create
    permission, create user, create user group, add user to user group, 
    give user group specified permission on the parent node

    Returns a dictionary of the format: {
        "node": Node,
        "permission": Permission,
        "user_group": UserGroup,
        "user": User,
    }
    """

    node = create_random_node(db, created_by_id=1, node_type=node_type)
    crud.node.instantiate_permissions(db, node=node)
    permission = crud.node.get_permission(
        db, id=node.id, permission_type=permission_type
    )
    user = create_random_user(db)
    user_group = create_random_user_group(db, created_by_id=1, node_id=node.id)
    crud.user_group.add_user_to_group(db, user_group=user_group, user_id=user.id)
    crud.user_group.add_permission(
        db, user_group=user_group, permission=permission, enabled=permission_enabled
    )
    return {
        "node": node,
        "permission": permission,
        "user_group": user_group,
        "user": user,
    }