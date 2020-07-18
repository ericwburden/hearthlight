import logging

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Network])
def read_networks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve networks.
    """
    networks = crud.network.get_multi(db, skip=skip, limit=limit)
    return networks


@router.post("/", response_model=schemas.Network)
def create_network(
    *,
    db: Session = Depends(deps.get_db),
    network_in: schemas.NetworkCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new network.
    """
    logging.info(network_in)
    network = crud.network.create(
        db=db, obj_in=network_in, created_by_id=current_user.id
    )
    return network


@router.put("/{id}", response_model=schemas.Network)
def update_network(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    network_in: schemas.NetworkUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an network.
    """
    network = crud.network.get(db=db, id=id)
    if not network:
        raise HTTPException(status_code=404, detail="Network not found")
    network = crud.network.update(db=db, db_obj=network, obj_in=network_in)
    return network


@router.get("/{id}", response_model=schemas.Network)
def read_network(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get network by ID.
    """
    network = crud.network.get(db=db, id=id)
    if not network:
        raise HTTPException(status_code=404, detail="Network not found")
    return network


@router.delete("/{id}", response_model=schemas.Network)
def delete_network(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an network.
    """
    network = crud.network.get(db=db, id=id)
    if not network:
        raise HTTPException(status_code=404, detail="Network not found")
    network = crud.network.remove(db=db, id=id)
    return network
