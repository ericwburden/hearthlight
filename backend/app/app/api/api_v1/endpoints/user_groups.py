from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()
node_update_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.node, schemas.PermissionTypeEnum.update
)

user_group_create_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.node, schemas.PermissionTypeEnum.create
)
user_group_read_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.user_group, schemas.PermissionTypeEnum.read
)
user_group_update_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.user_group, schemas.PermissionTypeEnum.update
)


@router.post("/", response_model=schemas.UserGroup)
def create_user_group(
    *,
    db: Session = Depends(deps.get_db),
    user_group_in: schemas.UserGroupCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
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
    """Endpoint to read a single user group. In order to read a
    user group, the user group must exist and the user must have read
    permissions for that user group or be a superuser.

    ## Args:

    - resource_id (int): databaase ID for the user group
    - db (Session, optional): SQLAlchemy Session. Defaults to Depends(deps.get_db).
    - current_user (models.User, optional): User object for the
    authenticated user. Defaults to Depends(user_group_read_validator).

    ## Raises:

    - HTTPException: 404 - When the resource_id refers to a user group
    that does not exist
    - HTTPException: 403 - When the user does not have read permissions
    for the user group

    ## Returns:

    models.UserGroup: the fetched UserGroup
    """

    user_group = crud.user_group.get(db=db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Cannot find user group.")
    return user_group


@router.get("/", response_model=List[schemas.UserGroup])
def read_user_groups(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[models.UserGroup]:
    """# Read a list of nodes

    Returns nodes in descending primary key order by default

    ## Args:

    - db (Session, optional): SQLAlchemy Session, injected. Defaults
    to Depends(deps.get_db).
    - skip (int, optional): Number of records to skip. Defaults to 0.
    - limit (int, optional): Number of records to retrieve. Defaults
    to 100.
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_user).

    ## Returns:

    - List[Node]: List of retrieved nodes
    """
    if crud.user.is_superuser(current_user):
        user_groups = crud.user_group.get_multi(db, skip=skip, limit=limit)
    else:
        user_groups = crud.user_group.get_multi_with_permissions(
            db, user=current_user, skip=skip, limit=limit
        )

    return user_groups


@router.put("/{resource_id}", response_model=schemas.UserGroup)
def update_node(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    user_group_in: schemas.UserGroupUpdate,
    current_user: models.User = Depends(user_group_update_validator),
) -> models.UserGroup:

    user_group = crud.user_group.get(db=db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Cannot find user group.")
    if user_group_in.node_id:
        parent_node = crud.node.get(db=db, id=user_group_in.node_id)
        if not parent_node:
            raise HTTPException(status_code=404, detail="Cannot find input parent node.")

        # This checks update permissions on the proposed new parent node,
        # which is required to reassign the parent. Update checks on
        # the node being updated are handled by the injected current_user 
        user_has_parent_permission = node_update_validator.check_permission(
            node_in.parent_id, db, current_user
        )
        if not user_has_parent_permission and not current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"User does not have permission to assign"
                    f" resources to node {node_in.parent_id}"
                ),
            )
    user_group = crud.user_group.update(
        db=db, db_obj=user_group, obj_in=user_group_in, updated_by_id=current_user.id
    )
    return user_group
