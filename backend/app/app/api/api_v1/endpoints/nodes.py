from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Node])
def read_nodes(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve nodes.
    """
    if crud.user.is_superuser(current_user):
        nodes = crud.node.get_multi(db, skip=skip, limit=limit)
    else:
        nodes = crud.node.get_multi_by_owner(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return nodes


@router.post("/", response_model=schemas.Node)
def create_node(
    *,
    db: Session = Depends(deps.get_db),
    node_in: schemas.NodeCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new node.
    """
    if node_in.parent_id and node_in.node_type == "network":
        raise HTTPException(
            status_code=400, detail="New networks should not have a parent node"
        )

    if not current_user.is_superuser and node_in.node_type == "network":
        raise HTTPException(
            status_code=403, detail="Only superusers can create new networks."
        )
    node = crud.node.create(db=db, obj_in=node_in, created_by_id=current_user.id)
    return node


@router.put("/{id}", response_model=schemas.Node)
def update_node(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    node_in: schemas.NodeUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an node.
    """
    node = crud.node.get(db=db, id=id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    if not crud.user.is_superuser(current_user) and (node.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    node = crud.node.update(db=db, db_obj=node, obj_in=node_in)
    return node


@router.get("/{id}", response_model=schemas.Node)
def read_node(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get node by ID.
    """
    node = crud.node.get(db=db, id=id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    if not crud.user.is_superuser(current_user) and (node.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
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
