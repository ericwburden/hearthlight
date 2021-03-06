from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from app import crud, models, schemas
from app.api import deps
from app.crud.base import GenericModelList
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


# --------------------------------------------------------------------------------------
# region | Endpoints for basic CRUD ----------------------------------------------------
# --------------------------------------------------------------------------------------


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


@router.get("/", response_model=GenericModelList[schemas.UserGroup])
def read_user_groups(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = "",
    sort_desc: Optional[bool] = None,
    name: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> GenericModelList[schemas.UserGroup]:
    """# Read a list of nodes

    Returns nodes in descending primary key order by default

    ## Args:

    - db (Session, optional): SQLAlchemy Session, injected. Defaults
    to Depends(deps.get_db).
    - skip (int, optional): Number of records to skip. Defaults to 0.
    - limit (int, optional): Number of records to retrieve. Defaults
    to 100.
    - sort_by (str, optional): Name of a column to sort by.
    - sort_desc (bool, optional): Should the column be sorted
    descending (true) or ascending (false).
    - name (str, optional): Filter the results by user group name, via
    name ILIKE "%name%"
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_user).

    ## Returns:

    - List[Node]: List of retrieved nodes
    """
    search = {k: v for k, v in {"name": name}.items() if v}
    if crud.user.is_superuser(current_user):
        user_groups = crud.user_group.get_multi(
            db,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_desc=sort_desc,
            search=search,
        )
    else:
        user_groups = crud.user_group.get_multi_with_permissions(
            db,
            user=current_user,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_desc=sort_desc,
            search=search,
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


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Endpoints for managing user group permissions -------------------------------
# --------------------------------------------------------------------------------------


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
    """# Grant multiple permissions to a user group

    In order to grant a permission to a user group, the permission must
    be for a resource that is attached to a node at or lower in the
    node hierarchy than the parent node for the user group. This
    prevents a user group from having permissions to perform CRUD
    operations on a parent resource, enforcing permissions to follow
    the node hierarchy. This needs to be true for all permissions in
    the bulk operation.

    ## Args:

    - resource_id (int): Primary key id for the user group
    - permissions (List[schemas.Permission]): List of permission objects
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(user_group_update_validator).

    ## Raises:

    - HTTPException: 404 - When one or more of the referenced
    permissions is no longer in the database
    - HTTPException: 403 - When one or more of the referenced
    permissions is not descended from the root node
    - HTTPException: 404 - When the user group referenced is not in the
    database
    - HTTPException: 403 - When the user does not have update
    permissions for the user group

    ## Returns:

    - schemas.Msg: A success message
    """
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
    """# Revoke multiple permissions in a user group

    The only requirements to revoke a permission in a user group are
    that the user group and permission indicated must both be in the
    database and the permission needs to be in the user group already.
    This needs to be true for all permissions in the bulk operation.

    ## Args:

    - resource_id (int): Primary key id for the user group
    - permissions (List[schemas.Permission]): List of permission objects
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(user_group_update_validator).

    ## Raises:

    - HTTPException: 404 - When one or more of the referenced
    permissions is no longer in the database
    - HTTPException: 404 - When one or more of the referenced
    permissions is not in the user group
    - HTTPException: 404 - When the user group referenced is not in the
    database
    - HTTPException: 403 - When the user does not have update
    permissions for the user group

    ## Returns:

    - schemas.Msg: A success message
    """
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
            status_code=404, detail="One or more permissions not in user group."
        )
    msg = f"Revoked {len(permissions)} permissions in UserGroup {resource_id}."
    return schemas.Msg(msg=msg)


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Endpoints for managing user group users -------------------------------------
# --------------------------------------------------------------------------------------


@router.get("/{resource_id}/users/{user_id}", response_model=schemas.UserGroupUser)
def add_user_to_user_group(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    user_id: int,
    current_user: models.User = Depends(user_group_update_validator),
) -> models.UserGroupUserRel:
    """# Add a user to a user group

    Users receive permission to access and perform operations on
    resources through associate with a user group. In order to be added
    to a user group, the user must exist in the database, the user
    group must exist in the database, and the user attempting to add
    the user to the user group must have update permissions on the
    user group (or be a superuser).

    ## Args:

    - resource_id (int): Primary key id for the user group
    - user_id (int): Primary key id for the user
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(user_group_update_validator).

    ## Raises:

    - HTTPException: 404 - When the user group referenced is not in the
    database
    - HTTPException: 404 - When the user referenced is not in the
    database
    - HTTPException: 403 - When the user doesn't have update permissions
    for the user group

    ## Returns:

    - models.UserGroupUserRel: An object representing the relationship
    between the user and user group
    """

    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Can not find user.")

    user_group = crud.user_group.get(db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Can not find user group.")
    user_group_user = crud.user_group.add_user(
        db, user_group=user_group, user_id=user_id
    )
    return user_group_user


@router.put("/{resource_id}/users/", response_model=List[schemas.UserGroupUser])
def add_multiple_users_to_user_group(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    user_ids: List[int],
    current_user: models.User = Depends(user_group_update_validator),
) -> List[models.UserGroupUserRel]:
    """# Add multiple users to a user group

    Users receive permission to access and perform operations on
    resources through associate with a user group. In order to be added
    to a user group, the user must exist in the database, the user
    group must exist in the database, and the user attempting to add
    the user to the user group must have update permissions on the
    user group (or be a superuser).

    ## Args:

    - resource_id (int): Primary key id for the user group
    - user_ids (List[int]): Primary key ids for the users to add
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(user_group_update_validator).

    ## Raises:

    - HTTPException: 404 - When the user group referenced is not in the
    database
    - HTTPException: 404 - When the one or more of the users referenced
    are not in the database
    - HTTPException: 403 - When the user doesn't have update permissions
    for the user group

    ## Returns:

    - List[models.UserGroupUserRel]: A list of objects representing the
    relationships between users and the user group
    """

    users_in_db = crud.user.get_filtered(db, ids=user_ids)
    if set(user_ids) != set([u.id for u in users_in_db]):
        raise HTTPException(status_code=404, detail="Can not find one or more users.")

    user_group = crud.user_group.get(db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Can not find user group.")
    user_group_users = crud.user_group.add_users(
        db, user_group=user_group, user_ids=user_ids
    )
    return user_group_users


@router.delete("/{resource_id}/users/{user_id}", response_model=schemas.User)
def remove_user_from_user_group(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    user_id: int,
    current_user: models.User = Depends(user_group_update_validator),
) -> models.User:
    """# Remove a user from a user group

    Remove the relationship between a user and a user group. In order
    to perform this operation, the user must exist in the database, the
    user group must exist in the database, the user must have an active
    relationship with the user group, and the user attempting to remove
    the user must have update permissions for the user group.

    ## Args:

    - resource_id (int): Primary key id for the user group
    - user_id (int): Primary key id for the user
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(user_group_update_validator).

    ## Raises:

    - HTTPException: 404 - When the user group referenced is not in the
    database
    - HTTPException: 404 - When the user referenced is not in the
    database
    - HTTPException: 404 - When the user referenced is not associated
    with the user group
    - HTTPException: 403 - When the user doesn't have update permissions
    for the user group

    ## Returns:

    - models.UserGroup: The user group object
    """

    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Can not find user.")

    user_group = crud.user_group.get(db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Can not find user group.")

    if user not in user_group.users:
        raise HTTPException(
            status_code=404, detail=f"User {user.id} not in user group {user_group.id}"
        )

    user_group_user = crud.user_group.remove_user(db, user_group=user_group, user=user)
    return user_group_user


@router.delete("/{resource_id}/users/", response_model=List[schemas.User])
def remove_multiple_users_from_user_group(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    user_ids: List[int],
    current_user: models.User = Depends(user_group_update_validator),
) -> List[models.User]:
    """# Remove a multiple users from a user group

    Remove the relationship between multiple users and a user group. In
    order to perform this operation, the user must exist in the
    database, the user group must exist in the database, the user must
    have an active relationship with the user group, and the user
    attempting to remove the user must have update permissions for the
    user group.

    ## Args:

    - resource_id (int): Primary key id for the user group
    - user_ids (List[int]): Primary key ids for the users to remove
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(user_group_update_validator).

    ## Raises:

    - HTTPException: 404 - When the user group referenced is not in the
    database
    - HTTPException: 404 - When one or more of the users referenced are
    not in the database
    - HTTPException: 404 - When one or more of the users referenced are
    not associated with the user group
    - HTTPException: 403 - When the user doesn't have update permissions
    for the user group

    ## Returns:

    - models.UserGroup: The user group object
    """

    user_group = crud.user_group.get(db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Can not find user group.")

    users = crud.user.get_filtered(db, ids=user_ids)
    stored_user_ids = [user.id for user in users]
    if set(user_ids) != set(stored_user_ids):
        raise HTTPException(status_code=404, detail="Can not find one or more users.")

    user_in_user_group_checks = ((user, user in user_group.users) for user in users)
    for user_in_user_group in user_in_user_group_checks:
        if not user_in_user_group[1]:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"User {user_in_user_group[0].id} not in user "
                    f"group {user_group.id}"
                ),
            )

    user_group_user = crud.user_group.remove_users(
        db, user_group=user_group, users=users
    )
    return user_group_user


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Endpoints for fetching users in/out of user group ---------------------------
# --------------------------------------------------------------------------------------


@router.get("/{resource_id}/users/", response_model=GenericModelList[schemas.User])
def read_users_in_group(
    resource_id: int,
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = "",
    sort_desc: Optional[bool] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(user_group_read_validator),
) -> GenericModelList[schemas.User]:
    """# Fetch users in a User Group

    Returns a list of users with a relationship to the indicated user
    group. Note, in order to read these users, the requesting user
    must either be a superuser or have read permission for the user
    group. This also means a user with user group read permissions
    can fetch users records they may not have read access for
    otherwise.

    ## Args:

    - resource_id (int): Primary key ID for the User Group
    - skip (int, optional): Number of records to skip. Defaults to 0.
    - limit (int, optional): Number of records to retrieve. Defaults
    to 100.
    - sort_by (str, optional): Name of a column to sort by.
    - sort_desc (bool, optional): Should the column be sorted
    descending (true) or ascending (false).
    - db (Session, optional): SQLAlchemy Session, injected. Defaults
    to Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(user_group_read_validator).

    ## Raises:

    - HTTPException: 404 - When the referenced User Group does not exist
    in the database.
    - HTTPException: 403 - When the user doesn't have read permissions
    for the user group.

    ## Returns:

    - GenericModelList[schemas.User]: Object containing a count of
    returned records and the records returned.
    """

    user_group = crud.user_group.get(db=db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Cannot find user group.")
    return crud.user.get_multi_in_group(
        db,
        user_group_id=user_group.id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )


@router.get("/{resource_id}/not/users/", response_model=GenericModelList[schemas.User])
def read_users_not_in_group(
    resource_id: int,
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = "",
    sort_desc: Optional[bool] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> GenericModelList[schemas.User]:
    """# Fetch users not in a User Group

    Returns a list of users who DO NOT have a relationship to the
    indicated user group. This endpoint is only available to
    superusers since it potentially grants access to the entire
    user base.

    ## Args:

    - resource_id (int): Primary key ID for the User Group
    - skip (int, optional): Number of records to skip. Defaults to 0.
    - limit (int, optional): Number of records to retrieve. Defaults
    to 100.
    - sort_by (str, optional): Name of a column to sort by.
    - sort_desc (bool, optional): Should the column be sorted
    descending (true) or ascending (false).
    - db (Session, optional): SQLAlchemy Session, injected. Defaults
    to Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 404 - When the referenced User Group does not exist
    in the database.
    - HTTPException: 400 - When the user accessing the endpoint is not a
    superuser.

    ## Returns:

    - GenericModelList[schemas.User]: Object containing a count of
    returned records and the records returned.
    """

    user_group = crud.user_group.get(db=db, id=resource_id)
    if not user_group:
        raise HTTPException(status_code=404, detail="Cannot find user group.")
    return crud.user.get_multi_not_in_group(
        db,
        user_group_id=user_group.id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
