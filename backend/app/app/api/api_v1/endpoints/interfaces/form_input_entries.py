from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from typing import Dict, Any, List

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


@router.post("/{resource_id}/entries/", response_model=Dict[str, Any])
def create_form_input_entry(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    form_input_entry_in: Dict[str, Any] = Body(...),
    current_user: models.User = Depends(interface_create_validator),
) -> BaseModel:
    """# Create an entry in a form input backing table

    Based on a FormInput schema (~/interfaces/form-inputs/{id}/schema),
    create a new entry in a FormInputInterface backing table. If the
    information passed in does not match the backing table schema,
    Pydantic will raise a ValidationError. The user must either have
    create permissions on the form input interface or be a superuser.

    ## Args:

    - resource_id (int): Primary key ID for the form input interface
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - form_input_entry_in (Dict[str, Any], optional): Dict of data to
    enter into the form input's table. Must match the schema for the
    backing table. Defaults to Body(...).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 404 - When attempting to add data to a form
    input interface that doesn't exist.
    - HTTPException: 403 - When attempting to add data to a form
    input interface when the backing table hasn't been created yet.
    - HTTPException: 422 - When the schema provided doesn't match
    the structure of the backing table.
    - HTTPException: 403 - When the user is a normal user and doesn't
    have create permissions for the form input interface.

    ## Returns:

    - BaseModel: The entry created, will match the schema for the form
    input interface backing table.
    """
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


@router.get("/{resource_id}/entries/{entry_id}", response_model=Dict[str, Any])
def read_form_input_entry(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    entry_id: int,
    current_user: models.User = Depends(interface_read_validator),
) -> BaseModel:
    """# Read one created form input entry

    In order to read from the form input interface's backing table, the
    user needs to either have read permissions on the form input or be
    a superuser.

    ## Args:

    - resource_id (int): Primary key ID for the form input interface
    - entry_id (int): Primary key ID for the form input interface table
    entry.
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 404 - When attempting to read from a form input
    interface that doesn't exist.
    - HTTPException: 403 - When attempting to read from a form input
    interface whose backing table hasn't been created.
    - HTTPException: 404 - When attempting to read a form input entry
    that doesn't exist.
    - HTTPException: 403 - When the user doesn't have read permissions
    on the form input interface.

    ## Returns:

    - BaseModel: The fetched entry, will match the schema for the form
    input interface backing table.
    """
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


@router.get("/{resource_id}/entries/", response_model=List[Dict[str, Any]])
def read_form_inputs(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(interface_read_validator),
) -> List[BaseModel]:
    """# Read multiple form input entries

    Read multiple entries from the form input interface backing table.
    The user must either have read permissions on the form input
    interface or be a superuser.

    ## Args:

    - resource_id (int): Primary key ID for the form input interface
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - skip (int, optional): The number of records to skip. Defaults
    to 0.
    - limit (int, optional): The maximum number of records to retrieve.
    Defaults to 100.
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ##Raises:

    - HTTPException: 404 - When attempting to read entries from a form
    input interface that doesn't exist.
    - HTTPException: 403 - When attempting to read entries for a form
    intput interface whose backing table hasn't been created yet.
    - HTTPException: 403 - When the user doesn't have read permissions
    for the form input interface.

    ## Returns:

    - List[BaseModel]: A list of form input entries. These will match
    the schema of the form input interface backing table.
    """
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


@router.put("/{resource_id}/entries/{entry_id}", response_model=Dict[str, Any])
def update_form_input(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    entry_id: int,
    form_input_in: Dict[str, Any] = Body(...),
    current_user: models.User = Depends(interface_update_validator),
) -> BaseModel:
    """# Update a form input interface entry

    Based on a FormInput schema (~/interfaces/form-inputs/{id}/schema),
    update an entry in a FormInputInterface backing table. If the
    information passed in does not match the backing table schema,
    Pydantic will raise a ValidationError. The user must either have
    update permissions on the form input interface or be a superuser.

    ## Args:

    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - resource_id (int): Primary key ID for the form input interface
    - entry_id (int): Primary key ID for the form input interface table
    entry.
    - form_input_entry_in (Dict[str, Any], optional): Dict of data to
    enter into the form input's table. Must match the schema for the
    backing table. Defaults to Body(...).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 404 - When attempting to update an entry in a form
    input interface that doesn't exist.
    - HTTPException: 403 - When attempting to update an entry in a form
    input interface whose backing table hasn't been created.
    - HTTPException: 404 - When attempting to update a form input entry
    that doesn't exist.
    - HTTPException: 403 - When the user doesn't have update permissions
    on the form input interface.

    ## Returns:

    - BaseModel: The updated form input entry, will match the schema for
    the form input interface backing table.
    """
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


@router.delete("/{resource_id}/entries/{entry_id}", response_model=Dict[str, Any])
def delete_form_input(
    *,
    db: Session = Depends(deps.get_db),
    resource_id: int,
    entry_id: int,
    current_user: models.User = Depends(interface_delete_validator),
) -> BaseModel:
    """# Delete a form input interface entry

    In order to delete from the form input interface's backing table,
    the user needs to either have delete permissions on the form input
    or be a superuser.

    ## Args:

    - resource_id (int): Primary key ID for the form input interface
    - entry_id (int): Primary key ID for the form input interface table
    entry.
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 404 - When attempting to delete from a form input
    interface that doesn't exist.
    - HTTPException: 403 - When attempting to delete from a form input
    interface whose backing table hasn't been created.
    - HTTPException: 404 - When attempting to delete a form input entry
    that doesn't exist.
    - HTTPException: 403 - When the user doesn't have delete permissions
    on the form input interface.

    ## Returns:

    - BaseModel: The deleted form input entry, will match the schema for
    the form input interface backing table.
    """
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
