from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from typing import Dict, Any

from app import crud, models, schemas
from app.api import deps

interface_read_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.interface, schemas.PermissionTypeEnum.read
)
interface_create_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.interface, schemas.PermissionTypeEnum.create
)

router = APIRouter()

@router.post("/{resource_id}/form-input")
def create_form_input(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    form_input_in: Dict[str, Any] = Body(...),
    current_user: models.User = Depends(interface_create_validator)
) -> BaseModel:
    interface = crud.interface.get(db, id=resource_id)
    if not interface:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    if not interface.table_created:
        raise HTTPException(
            status_code=403, 
            detail="The backing table for this interface has not been created."
        )
    form_input_crud = crud.interface.get_interface_crud(db, id=resource_id)
    try:
        form_input = form_input_crud.create(db, obj_in=form_input_in)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    return form_input

@router.get("/{resource_id}/form-input/{form_input_id}")
def read_form_input(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    form_input_id: int,
    current_user: models.User = Depends(interface_read_validator)
) -> BaseModel:
    interface = crud.interface.get(db, id=resource_id)
    if not interface:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    if not interface.table_created:
        raise HTTPException(
            status_code=403, 
            detail="The backing table for this interface has not been created."
        )
    form_input_crud = crud.interface.get_interface_crud(db, id=resource_id)
    form_input = form_input_crud.get(db, id=form_input_id)
    if not form_input:
        raise HTTPException(status_code=404, detail="Cannot find form input.")
    return form_input