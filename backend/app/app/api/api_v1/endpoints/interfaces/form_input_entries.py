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
interface_update_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.interface, schemas.PermissionTypeEnum.update
)
interface_delete_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.interface, schemas.PermissionTypeEnum.delete
)

router = APIRouter()


@router.post("/{resource_id}/entries/")
def create_form_input_entry(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    form_input_entry_in: Dict[str, Any] = Body(...),
    current_user: models.User = Depends(interface_create_validator),
) -> BaseModel:
    form_input = crud.form_input.get(db, id=resource_id)
    if not form_input:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    if not form_input.table_created:
        raise HTTPException(
            status_code=403,
            detail="The backing table for this interface has not been created.",
        )
    form_input_crud = crud.form_input.get_table_crud(db, id=resource_id)
    try:
        form_input_entry = form_input_crud.create(db, obj_in=form_input_entry_in)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    return form_input_entry


@router.get("/{resource_id}/entries/{entry_id}")
def read_form_input_entry(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    entry_id: int,
    current_user: models.User = Depends(interface_read_validator),
) -> BaseModel:
    form_input = crud.form_input.get(db, id=resource_id)
    if not form_input:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    if not form_input.table_created:
        raise HTTPException(
            status_code=403,
            detail="The backing table for this interface has not been created.",
        )
    form_input_crud = crud.form_input.get_table_crud(db, id=resource_id)
    form_input_entry = form_input_crud.get(db, id=entry_id)
    if not form_input_entry:
        raise HTTPException(status_code=404, detail="Cannot find form input entry.")
    return form_input_entry


@router.get("/{resource_id}/entries/")
def read_form_inputs(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(interface_read_validator),
) -> BaseModel:
    form_input = crud.form_input.get(db, id=resource_id)
    if not form_input:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    if not form_input.table_created:
        raise HTTPException(
            status_code=403,
            detail="The backing table for this interface has not been created.",
        )
    form_input_crud = crud.form_input.get_table_crud(db, id=resource_id)
    form_input_entries = form_input_crud.get_multi(db, skip=skip, limit=limit)
    return form_input_entries


@router.put("/{resource_id}/entries/{entry_id}")
def update_form_input(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    entry_id: int,
    form_input_in: Dict[str, Any] = Body(...),
    current_user: models.User = Depends(interface_update_validator),
) -> BaseModel:
    form_input = crud.form_input.get(db, id=resource_id)
    if not form_input:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    if not form_input.table_created:
        raise HTTPException(
            status_code=403,
            detail="The backing table for this interface has not been created.",
        )
    form_input_crud = crud.form_input.get_table_crud(db, id=resource_id)
    form_input_entry = form_input_crud.get(db, id=entry_id)
    if not form_input_entry:
        raise HTTPException(status_code=404, detail="Cannot find form input record.")
    form_input_entry = form_input_crud.update(
        db, db_obj=form_input_entry, obj_in=form_input_in
    )
    return form_input_entry


@router.delete("/{resource_id}/entries/{entry_id}")
def delete_form_input(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    entry_id: int,
    current_user: models.User = Depends(interface_delete_validator),
) -> BaseModel:
    form_input = crud.form_input.get(db, id=resource_id)
    if not form_input:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    if not form_input.table_created:
        raise HTTPException(
            status_code=403,
            detail="The backing table for this interface has not been created.",
        )
    form_input_crud = crud.form_input.get_table_crud(db, id=resource_id)
    form_input_entry = form_input_crud.get(db, id=entry_id)
    if not form_input_entry:
        raise HTTPException(status_code=404, detail="Cannot find form input entry.")
    form_input_entry = form_input_crud.remove(db, id=entry_id)
    return form_input_entry
