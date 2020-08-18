from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()
user_group_create_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.node, schemas.PermissionTypeEnum.create
)
user_group_read_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.user_group, schemas.PermissionTypeEnum.read
)


@router.post("/", response_model=schemas.UserGroup)
def create_user_group(
    *,
    db: Session = Depends(deps.get_db),
    user_group_in: schemas.UserGroupCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> models.UserGroup:
    """# Create a new user group.

    UserGroups are the mechanism by which Users and their Permissions
    are related to Nodes and other structural objects. The validation 
    rule in place are:
    - A new UserGroup must be attached to an existing Node
    - The parent Node must be active
    - The User, if not a superuser, must have create permissions on the
    parent Node

    ##Args:

    - user_group_in (schemas.UserGroupCreate): Object specifying the
    attributes of the user group to create.
    - db (Session, optional): SQLAlchemy session. Defaults to 
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the 
    authenticated user. Defaults to Depends(deps.get_current_active_user).

    ##Raises:

    - HTTPException: 404 - When the node_id references a node that does
    not exist
    - HTTPException: 403 - When the parent node is inactive
    - HTTPException: 403 - When the user does not have create permission
    on the parent node.

    ##Returns:
        
    - models.UserGroup: the created UserGroup
    """
    # Fail if the node for node_id doesn't exist
    node = crud.node.get(db, id=user_group_in.node_id)
    if not node:
        raise HTTPException(
            status_code=404, detail="Cannot find node indicated by node_id."
        )

    # Fail if the node is inactive
    if not node.is_active:
        raise HTTPException(
            status_code=403, detail="Cannot add user group to an inactive node."
        )

    # Fail if normal user doesn't have create permission on parent node
    user_has_permission = user_group_create_validator.check_permission(
        user_group_in.node_id, db, current_user
    )
    if not user_has_permission and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="User does not have permission to create this node.",
        )

    user_group = crud.user_group.create(
        db, obj_in=user_group_in, created_by_id=current_user.id
    )
    return user_group


@router.get("/{resource_id}", response_model=schemas.UserGroup)
def read_user_group(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    current_user: models.User = Depends(user_group_read_validator),
) -> models.UserGroup:

    user_group = crud.user_group.get(db=db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Cannot find user group.")
    return user_group
