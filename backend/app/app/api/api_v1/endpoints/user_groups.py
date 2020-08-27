from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from app import crud, models, schemas
from app.api import deps
from app.crud.errors import MissingRecordsError

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
user_group_delete_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.user_group, schemas.PermissionTypeEnum.delete
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
def update_user_group(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    user_group_in: schemas.UserGroupUpdate,
    current_user: models.User = Depends(user_group_update_validator),
) -> models.UserGroup:
    """# Update a user group

    ## Args:

    - resource_id (int): Primary key ID for the user group to update
    - user_group_in (schemas.UserGroupUpdate): Object specifying the attributes
    of the user group to update.
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(user_group_update_validator).

    ## Raises:

    - HTTPException: 404 - When the user group identified by
    'resource_id' does not exist.
    - HTTPException: 404 - When the node_id in user_group_in refers to
    a user group that does not exist.
    - HTTPException: 403 - When the user does not have update
    permissions on the user group.
    - HTTPException: 403 - When the user does not have update
    permission on the new parent node when attempting to reassign
    node_id

    ## Returns:

    - models.UserGroup: the updated UserGroup
    """

    user_group = crud.user_group.get(db=db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Cannot find user group.")
    if user_group_in.node_id:
        parent_node = crud.node.get(db=db, id=user_group_in.node_id)
        if not parent_node:
            raise HTTPException(
                status_code=404, detail="Cannot find input parent node."
            )

        # This checks update permissions on the proposed new parent node,
        # which is required to reassign the parent. Update checks on
        # the node being updated are handled by the injected current_user
        user_has_parent_permission = node_update_validator.check_permission(
            user_group_in.node_id, db, current_user
        )
        if not user_has_parent_permission and not current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"User does not have permission to assign"
                    f" resources to node {user_group_in.node_id}"
                ),
            )
    user_group = crud.user_group.update(
        db=db, db_obj=user_group, obj_in=user_group_in, updated_by_id=current_user.id
    )
    return user_group


@router.delete("/{resource_id}", response_model=schemas.UserGroup)
def delete_user_group(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    current_user: models.User = Depends(user_group_delete_validator),
) -> Any:
    """# Delete a user group

    When deleting a user group, any permissions *for* that user group
    are also deleted, along with any association table entries. The
    user must either have delete permissions on the user group or be
    a superuser.

    ## Args:

    - resource_id (int): Primary key ID for the user group to delete.
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to Depends(user_group_delete_validator).

    ## Raises:

    - HTTPException: 404 - When the target user group is not in the database.
    - HTTPExceptoin: 403- When a normal user does not have delete permissions for the
    user_group.

    ## Returns:

    - UserGroup: The deleted UserGroup
    """
    user_group = crud.user_group.get(db=db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Cannot find user group.")
    user_group = crud.user_group.remove(db=db, id=resource_id)
    return user_group


@router.put("/{resource_id}/permissions/{permission_id}", response_model=schemas.Msg)
def grant_permission_to_user_group(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    permission_id: int,
    current_user: models.User = Depends(user_group_update_validator),
) -> schemas.Msg:
    """# Grant a permission to a user group

    In order to grant a permission to a user group, the permission must
    be for a resource that is attached to a node at or lower in the
    node hierarchy than the parent node for the user group. This
    prevents a user group from having permissions to perform CRUD
    operations on a parent resource, enforcing permissions to follow
    the node hierarchy.

    ## Args:

    - resource_id (int): Primary key id for the user group
    - permission_id (int): Primary key id for the permission to grant to
    the user group
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to Depends(user_group_update_validator).

    ## Raises:

    - HTTPException: 404 - When the indicated user group is not in the
    database
    - HTTPException: 404 - When the indicated permission is not in the
    database
    - HTTPException: 403 - When the indicated permission is for a
    resource that is not connected to a descendant of the user group's
    - HTTPException: 403 - When the user doesn't have update permission
    for the user group.

    ## Returns:

    - schemas.Msg: A success message
    """

    user_group = crud.user_group.get(db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Cannot find user group.")

    permission = crud.permission.get(db, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Cannot find permission.")

    # Check to be sure the permission is for a resource that the user
    # group has access to in the node tree
    is_descendant = crud.permission.in_node_descendants(
        db, node_id=user_group.node_id, permission=permission
    )
    if not is_descendant:
        raise HTTPException(
            status_code=403,
            detail=(
                f"{permission.resource_type} {permission.resource_id} is not descended "
                f"from node {user_group.node_id}"
            ),
        )

    crud.permission.grant(db, user_group_id=resource_id, permission_id=permission_id)
    msg = (
        f"Granted UserGroup {resource_id} '{permission.permission_type}'"
        f"permission on {permission.resource_type} {permission.resource_id}"
    )
    return schemas.Msg(msg=msg)


@router.delete("/{resource_id}/permissions/{permission_id}", response_model=schemas.Msg)
def revoke_permission_for_user_group(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    permission_id: int,
    current_user: models.User = Depends(user_group_update_validator),
) -> schemas.Msg:
    """# Revoke a permission in a user group

    The only requirements to revoke a permission in a user group are
    that the user group and permission indicated must both be in the
    database and the permission needs to be in the user group already.

    ## Args:

    - resource_id (int): Primary key id for the user group
    - permission_id (int): Primary key id for the permission to revoke in
    the user group
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to Depends(user_group_update_validator).

    ## Raises:

    - HTTPException: 404 - When the indicated user group is not in the
    database
    - HTTPException: 404 - When the indicated permission is not in the
    database
    - HTTPException: 4040 - When the indicated permission is not in the
    indicated user group
    - HTTPException: 403 - When the user doesn't have update permission
    for the user group.

    ## Returns:

    - schemas.Msg: A success message
    """
    user_group = crud.user_group.get(db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Cannot find user group.")

    permission = crud.permission.get(db, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Cannot find permission.")

    try:
        crud.permission.revoke(
            db, user_group_id=resource_id, permission_id=permission_id
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Permission not in user group.")

    msg = (
        f"Revoked '{permission.permission_type}' permission for "
        f"{permission.resource_type} {permission.resource_id} in "
        f"UserGroup {resource_id}"
    )
    return schemas.Msg(msg=msg)


@router.put("/{resource_id}/permissions/", response_model=schemas.Msg)
def grant_multiple_permissions_to_user_group(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    permissions: List[schemas.Permission],
    current_user: models.User = Depends(user_group_update_validator),
) -> schemas.Msg:
    user_group = crud.user_group.get(db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Cannot find user group.")

    permission_ids = [p.id for p in permissions]
    if not crud.permission.all_in_database(db, permission_ids=permission_ids):
        raise HTTPException(
            status_code=404, detail="Cannot find one or more permissions."
        )

    # Check to be sure all permissions are for a resource that the user
    # group has access to in the node tree
    all_descended = crud.permission.all_node_descendants(
        db, node_id=user_group.node_id, permissions=permissions
    )
    if not all_descended:
        detail = f"One or more permissions not descended from node {user_group.node_id}"
        raise HTTPException(status_code=403, detail=detail)

    crud.permission.grant_multiple(
        db, user_group_id=resource_id, permission_ids=permission_ids
    )
    msg = f"Granted {len(permissions)} permissions to UserGroup {resource_id}."
    return schemas.Msg(msg=msg)


@router.delete("/{resource_id}/permissions/", response_model=schemas.Msg)
def revoke_multiple_permission_for_user_group(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    permissions: List[schemas.Permission],
    current_user: models.User = Depends(user_group_update_validator),
) -> schemas.Msg:
    user_group = crud.user_group.get(db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Cannot find user group.")
    
    permission_ids = [p.id for p in permissions]
    if not crud.permission.all_in_database(db, permission_ids=permission_ids):
        raise HTTPException(
            status_code=404, detail="Cannot find one or more permissions."
        )
    try:
        crud.permission.revoke_multiple(
            db, user_group_id=resource_id, permission_ids=permission_ids
        )
    except MissingRecordsError:
        raise HTTPException(
            status_code=404, 
            detail="One or more permissions not in user group."
        )
    msg = f"Revoked {len(permissions)} permissions in UserGroup {resource_id}."
    return schemas.Msg(msg=msg)
