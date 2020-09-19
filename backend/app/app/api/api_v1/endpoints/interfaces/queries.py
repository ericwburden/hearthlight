from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app import crud, models, schemas
from app.api import deps


interface_read_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.interface, schemas.PermissionTypeEnum.read
)

router = APIRouter()


@router.post("/", response_model=schemas.Query)
def create_query_interface(
    *,
    db: Session = Depends(deps.get_db),
    query_in: schemas.QueryCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> models.QueryInterface:
    query = crud.query.create(db=db, obj_in=query_in, created_by_id=current_user.id)
    return query


@router.get("/{id}", response_model=schemas.Query)
def read_query_interface(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> models.QueryInterface:
    query = crud.query.get(db=db, id=id)
    if not query:
        raise HTTPException(status_code=404, detail="Cannot find query.")
    return query


@router.get("/", response_model=List[schemas.Query])
def read_query_interfaces(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> List[models.QueryInterface]:

    queries = crud.query.get_multi(db, skip=skip, limit=limit)
    return queries


@router.put("/{id}", response_model=schemas.Query)
def update_query_interface(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    query_in: schemas.QueryUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> models.QueryInterface:
    query = crud.query.get(db=db, id=id)
    if not query:
        raise HTTPException(status_code=404, detail="Cannot find query.")
    query = crud.query.update(
        db=db, db_obj=query, obj_in=query_in, updated_by_id=current_user.id
    )
    return query


@router.delete("/{id}", response_model=schemas.Query)
def delete_query_interface(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> models.QueryInterface:
    query = crud.query.get(db=db, id=id)
    if not query:
        raise HTTPException(status_code=404, detail="Cannot find query.")
    query = crud.query.remove(db=db, id=id)
    return query


@router.get("/{resource_id}/run", response_model=List[Dict[str, Any]])
def query_interface_run_query(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    page: int = 0,
    page_size: int = 25,
    current_user: models.User = Depends(interface_read_validator),
) -> List[Dict[str, Any]]:
    query = crud.query.get(db=db, id=resource_id)
    if not query:
        raise HTTPException(status_code=404, detail="Cannot find query.")
    query_result = crud.query.run_query(
        db=db, id=resource_id, page=page, page_size=page_size
    )
    return jsonable_encoder(query_result)
