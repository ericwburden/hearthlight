from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.crud.base import GenericModelList
from app.schemas.generic import get_generic_schema

router = APIRouter()

# These functions are for adding and modifying the available form input
# interface definitions, and are available only to the superuser.


@router.post("/", response_model=schemas.FormInput)
def create_form_input_interface(
    *,
    db: Session = Depends(deps.get_db),
    form_input_in: schemas.FormInputCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.FormInputInterface:
    """# Create a new interface specification

    This endpoint is only accessible to the superuser. In order to add
    a new form input interface, the name of the backing table must be
    unique.

    ## Args:

    - form_input_in (schemas.FormInputCreate): Specification for a new
    interface
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 400 - When the user attempting to access the
    endpoint is not a superuser
    - HTTPException: 400 - When attempting to create a new interface
    with a database backing table name for a table that already
    exists.

    ## Returns:

    - models.FormInput: The created FormInput
    """
    template_table_name = form_input_in.template.table_name
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name=template_table_name
    )
    if form_input:
        raise HTTPException(
            status_code=400,
            detail=(
                "A form input interface with that table name already exists, "
                "rename your template table."
            ),
        )
    form_input = crud.form_input.create(
        db=db, obj_in=form_input_in, created_by_id=current_user.id
    )
    return form_input


@router.get("/{id}", response_model=schemas.FormInput)
def read_form_input_interface(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.FormInputInterface:
    """# Read a form input interface specification by id

    ## Args:

    - id (int): Primary key ID for the interface to fetch.
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for
    the user accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 400 - When the user attempting to access the
    endpoint is not a superuser
    - HTTPException: 404 - When the target interface is not in the
    database

    ## Returns:

    - models.FormInputInterface: The fetched form input interface
    """
    form_input = crud.form_input.get(db=db, id=id)
    if not form_input:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    return form_input


@router.get("/", response_model=GenericModelList[schemas.FormInput])
def read_form_input_interfaces(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> GenericModelList[schemas.FormInput]:
    """# Read a list of form input specifications

    ## Args:

    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - skip (int, optional): Number of records to skip. Defaults to 0.
    - limit (int, optional): Number of records to retrieve. Defaults to
    100.
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 400 - When the user attempting to access the
    endpoint is not a superuser

    ## Returns:

    - List[models.FormInputInterface]: List of retrieved form input
    interfaces
    """
    form_inputs = crud.form_input.get_multi(db, skip=skip, limit=limit)
    return form_inputs


@router.put("/{id}", response_model=schemas.FormInput)
def update_form_input_interface(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    form_input_in: schemas.FormInputUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.FormInputInterface:
    """# Update a form input interface

    ## Args:

    - id (int): Primary key ID for the Interface to update.
    - form_input_in (schemas.FormInputUpdate): Object specifying the
    attributes of the interface to update.
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the
    user accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 400 - When the user attempting to access the
    endpoint is not a superuser
    - HTTPException: 404 - When the interface identified by 'id' does
    not exist in the databaes.

    ## Returns:

    - models.FormInputInterface: the updated form input interface
    """
    form_input = crud.form_input.get(db=db, id=id)
    if not form_input:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    if form_input_in.template and form_input.table_created:
        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot modify the table template, the table has already been created."
            ),
        )
    form_input = crud.form_input.update(
        db=db, db_obj=form_input, obj_in=form_input_in, updated_by_id=current_user.id
    )
    return form_input


@router.delete("/{id}", response_model=schemas.FormInput)
def delete_form_input_interface(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.FormInputInterface:
    """# Delete a form input interface

    ## Args:

    - id (int): Primary key ID for the form input interface to delete
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 400 - When the user attempting to access the
    endpoint is not a superuser
    - HTTPException: 404 - When the interface identified by 'id' is not
    in the database.

    ## Returns:

    - models.FormInputInterface: The deleted form input interface
    """
    form_input = crud.form_input.get(db=db, id=id)
    if not form_input:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    form_input = crud.form_input.remove(db=db, id=id)
    return form_input


@router.post("/{id}/build_table", response_model=schemas.FormInput)
def build_form_input_interface_table(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.FormInputInterface:
    """# Build the table from the form interface template

    Creates the table defined by template  in the database.
    In order to create the table, the identified interface must
    exist in the database and there can't be a table in the database
    with the same name as the table being created.

    ## Args:

    - id (int): Primary key ID for the FormInputInterface
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 404 - When the interface indicated by ID does
    not exist in the database.
    - HTTPException: 400 - When attempting to create a table and
    there is already a table in the database with that name.

    ## Returns:

    - models.FormInputInterface: The form interface post table-creation
    """
    form_input = crud.form_input.get(db=db, id=id)
    if not form_input:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    form_input = crud.form_input.create_template_table(db=db, id=id)
    return form_input


@router.get("/{id}/schema", response_model=Dict[str, Any])
def get_interface_schema(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """# Fetch the JSON schema for a form input interface backing table

    In order for a third-party application to know for sure what's in a
    backing table for a particular form input interface, it will need to
    use this endpoint. Returns a standard Pydantic schema.

    ## Args:

    - id (int): Primary key ID for the form input interface.
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 404 - When the interface indicate by the primary
    key is not represented in the database.
    - HTTPException: 403 - When the backing table for the indicated
    interface has not yet been created/finalized.

    ## Returns:

    - Dict[str, Any]: A Pydantic schema
    ([link](https://pydantic-docs.helpmanual.io/usage/schema/))
    """
    form_input = crud.form_input.get(db, id=id)
    if not form_input:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    if not form_input.table_created:
        raise HTTPException(
            status_code=403,
            detail="The backing table for this interface has not been created.",
        )
    table_name = form_input.template["table_name"]
    schema = get_generic_schema(table_name)
    return schema.schema()
