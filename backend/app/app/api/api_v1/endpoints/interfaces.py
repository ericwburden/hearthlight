import logging
from pydantic import BaseModel
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.schemas.generic import get_generic_schema

router = APIRouter()

# These functions are for adding and modifying the available interface
# definitions, and are available only to the superuser.


@router.post("/", response_model=schemas.Interface)
def create_interface(
    *,
    db: Session = Depends(deps.get_db),
    interface_in: schemas.InterfaceCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Interface:
    """# Create a new interface specification

    This endpoint is only accessible to the superuser. In order to add
    a new interface, the name of the backing table must be unique.

    ## Args:

    - interface_in (schemas.InterfaceCreate): Specification for a new
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

    - models.Interface: The created Interface
    """
    template_table_name = interface_in.table_template.table_name
    interface = crud.interface.get_by_template_table_name(
        db, table_name=template_table_name
    )
    if interface:
        raise HTTPException(
            status_code=400,
            detail=(
                "An interface with that table name already exists, "
                "rename your template table."
            ),
        )
    interface = crud.interface.create(
        db=db, obj_in=interface_in, created_by_id=current_user.id
    )
    return interface


@router.get("/{id}", response_model=schemas.Interface)
def read_interface(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Interface:
    """# Read an interface specification by id

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

    - models.Interface: The fetched Interface
    """
    interface = crud.interface.get(db=db, id=id)
    if not interface:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    return interface


@router.get("/", response_model=List[schemas.Interface])
def read_interfaces(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> List[models.Interface]:
    """# Read a list of Interfaces

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

    - List[models.Interface]: List of retrieved Interfaces
    """
    interfaces = crud.interface.get_multi(db, skip=skip, limit=limit)
    return interfaces


@router.put("/{id}", response_model=schemas.Interface)
def update_interface(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    interface_in: schemas.InterfaceUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Interface:
    """# Update an Interface

    ## Args:

    - id (int): Primary key ID for the Interface to update.
    - interface_in (schemas.InterfaceUpdate): Object specifying the
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

    - models.Interface: the updated Interface
    """
    interface = crud.interface.get(db=db, id=id)
    if not interface:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    if interface_in.table_template and interface.table_created:
        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot modify the table template, the table has already been created."
            ),
        )
    interface = crud.interface.update(
        db=db, db_obj=interface, obj_in=interface_in, updated_by_id=current_user.id
    )
    return interface


@router.delete("/{id}", response_model=schemas.Interface)
def delete_interface(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Interface:
    """# Delete an interface

    ## Args:

    - id (int): Primary key ID for the interface to delete
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

    - models.Interface: The deleted Interface
    """
    interface = crud.interface.get(db=db, id=id)
    if not interface:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    interface = crud.interface.remove(db=db, id=id)
    return interface


@router.post("/{id}/build_table", response_model=schemas.Interface)
def build_interface_table(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Interface:
    """# Build the table from the Interface table_template

    Creates the table defined by table_template  in the database.
    In order to create the table, the identified interface must
    exist in the database and there can't be a table in the database
    with the same name as the table being created.

    ## Args:

    - id (int): Primary key ID for the Interface
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

    - models.Interface: The Interface post table-creation
    """
    interface = crud.interface.get(db=db, id=id)
    if not interface:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    interface = crud.interface.create_template_table(db=db, id=id)
    return interface


@router.get("/{id}/schema", response_model=Dict[str, Any])
def get_interface_schema(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """# Fetch the JSON schema for a interface backing table

    In order for a third-party application to know for sure what's in a
    backing table for a particular interface, it will need to use this
    endpoint. Returns a standard Pydantic schema.

    ## Args:

    - id (int): Primary key ID for the interface.
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
    interface = crud.interface.get(db, id=id)
    if not interface:
        raise HTTPException(status_code=404, detail="Cannot find interface.")
    if not interface.table_created:
        raise HTTPException(
            status_code=403, 
            detail="The backing table for this interface has not been created."
        )
    table_name = interface.table_template['table_name']
    schema = get_generic_schema(table_name)
    return schema.schema()