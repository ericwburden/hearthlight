from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()
node_create_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.node, schemas.PermissionTypeEnum.create
)
node_read_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.node, schemas.PermissionTypeEnum.read
)
node_update_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.node, schemas.PermissionTypeEnum.update
)
node_delete_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.node, schemas.PermissionTypeEnum.delete
)


@router.post("/", response_model=schemas.Node)
def create_node(
    *,
    db: Session = Depends(deps.get_db),
    node_in: schemas.NodeCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> models.Node:
    """# Create a new node. 
    
    Nodes are the basic organizational structure and are organized in a
    tree-like hierarchy, with a 'network' node forming the root node 
    for a grouping of nodes. This provides a flexible organizational 
    structure where nodes can be nested arbitrarily deeply. There are a
    number of validation rules in place, including:
    - A 'network' node must have a node_type='network'
    - Network nodes must not have a parent_id specified
    - Only superusers can create networks
    - Any 'non-network' node (i.e. node_type!='network') must have a
    parent_id specified
    - The parent_id must refer to an existing node in the database
    - The node indicated by parent_id must be active (i.e., 
    is_active=True)
    - The user must belong to a user group with create permissions on 
    the parent node

    ## Args:

    - node_in (schemas.NodeCreate): Object specifying the attributes of
    the node to create
    - db (Session, optional): SQLAlchemy session. Defaults to 
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the 
    authenticated user. Defaults to Depends(deps.get_current_active_user).

    ## Raises:

    - HTTPException: 400 - When a 'network' node has a parent_id 
    specified
    - HTTPException: 403 - When a normal user attempts to create a 
    'network' node
    - HTTPException: 400 - When attempting to create a 'non-network' 
    node without a parent_id specified
    - HTTPException: 404 - When the parent_id doesn't match a node 
    in the database
    - HTTPException: 403 - When the node indicated by parent_id is 
    inactive
    - HTTPException: 403 - When a normal user attempts to create a node
    without create permissions on the parent

    ## Returns:

    - Node: the created Node
    """

    # Validation for creating network (root) nodes
    if node_in.node_type == "network":

        # Fail if attempting to create a 'network' node with a parent
        if node_in.parent_id:
            raise HTTPException(
                status_code=400, detail="New networks should not have a parent node"
            )

        # Fail if a non-superuser tries to create a 'network' node
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Only superusers can create new networks."
            )
    else:  # Validation for creating a non-network node

        # Fail if attempting to create a non-'network' node without a parent
        if not node_in.parent_id:
            raise HTTPException(
                status_code=400, detail="Cannot create a node without a parent."
            )

        # Fail if the node for parent_id doesn't exist
        parent = crud.node.get(db, id=node_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=404, detail="Cannot find node indicated by parent_id."
            )

        # Fail if the parent node is not active
        if not parent.is_active:
            raise HTTPException(
                status_code=403, detail="Cannot add a node to an inactive parent."
            )

        # Fail if normal user doesn't have create permission on parent node
        user_has_permission = node_create_validator.check_permission(
            node_in.parent_id, db, current_user
        )
        if not user_has_permission and not current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail="User does not have permission to create this node",
            )

    node = crud.node.create(db=db, obj_in=node_in, created_by_id=current_user.id)
    return node


@router.get("/{resource_id}", response_model=schemas.Node)
def read_node(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    current_user: models.User = Depends(node_read_validator),
) -> models.Node:
    """# Get a node by id

    ## Args:

    - resource_id (int): Primary key ID for the node
    - db (Session, optional): SQLAlchemy Session. Defaults to 
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to Depends(node_read_validator).

    ## Raises:

    - HTTPException: 404 - When the resource_id doesn't match a node in
    the database.
    - HTTPException: 403 - When the current user doesn't have permission
    to read the node indicated by resource_id.

    ## Returns:

    - Node: The Node with the primary id == resource_id
    """
    node = crud.node.get(db=db, id=resource_id)
    if not node:
        raise HTTPException(status_code=404, detail="Cannot find node.")
    return node


@router.get("/", response_model=List[schemas.Node])
def read_nodes(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[models.Node]:
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
    
    - List[models.Node]: List of retrieved nodes
    """
    if crud.user.is_superuser(current_user):
        nodes = crud.node.get_multi(db, skip=skip, limit=limit)
    else:
        nodes = crud.node.get_multi_with_permissions(
            db, user=current_user, skip=skip, limit=limit
        )

    return nodes


@router.put("/{resource_id}", response_model=schemas.Node)
def update_node(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    node_in: schemas.NodeUpdate,
    current_user: models.User = Depends(node_update_validator),
) -> Any:
    """
    Update an node.
    """

    node = crud.node.get(db=db, id=resource_id)
    if not node:
        raise HTTPException(status_code=404, detail="Cannot find node.")
    if node_in.parent_id:
        parent_node = crud.node.get(db=db, id=node_in.parent_id)
        if not parent_node:
            raise HTTPException(status_code=404, detail="Cannot find parent node.")

        user_has_permission = node_update_validator.check_permission(
            node_in.parent_id, db, current_user
        )
        if not user_has_permission and not current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail=f"User does not have permission to assign resources to node {node_in.parent_id}.",
            )
    node = crud.node.update(db=db, db_obj=node, obj_in=node_in, updated_by_id=current_user.id)
    return node


@router.delete("/{id}", response_model=schemas.Node)
def delete_node(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an node.
    """
    node = crud.node.get(db=db, id=id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    if not crud.user.is_superuser(current_user) and (node.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    node = crud.node.remove(db=db, id=id)
    return node
