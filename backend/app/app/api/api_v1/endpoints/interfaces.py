from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

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
