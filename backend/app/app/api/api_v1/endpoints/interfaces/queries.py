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
    """# Create a new query interface

    This endpoint is only available to superusers. Creates a new query
    interface. A query interface contains a JSON representation of a
    SQL query which can be run to return a result from the database.
    Note, this result will be runnable and readable by users who have
    read permissions on the query interface.

    ## Args:

    - query_in (schemas.QueryCreate): An object specifying the new query
    to create.
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 400 - When the user attempting to access the
    endpoint is not a superuser

    ## Returns:

    - models.QueryInterface: The created query interface.
    """
    query = crud.query.create(db=db, obj_in=query_in, created_by_id=current_user.id)
    return query


@router.get("/{id}", response_model=schemas.Query)
def read_query_interface(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> models.QueryInterface:
    """# Read one query interface

    Fetch the query interface directly. To fetch just the query result,
    user the ~/interfaces/queries/{resource_id}/run endpoint.

    ## Args:

    - id (int): Primary key id for the query interface
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 400 - When the user attempting to access the
    endpoint is not a superuser.
    - HTTPException: 404 - When attempting to fetch a query interface
    that doesn't exist.

    ## Returns:

    - models.QueryInterface: The fetched query interface.
    """
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
    """# Read multiple query interfaces

    Fetch mutliple query interfaces directly. To fetch just the query
    result, user the ~/interfaces/queries/{resource_id}/run endpoint.

    ## Args:

    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - skip (int, optional): The number of records to skip. Defaults
    to 0.
    - limit (int, optional): The maximum number of records to retrieve.
    Defaults to 100.
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 400 - When the user attempting to access the
    endpoint is not a superuser.

    ## Returns:

    - List[models.QueryInterface]: The fetched query interfaces.
    """
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
    """# Update a query interface

    Update a query interface. Note, if the query template is updated,
    running the query will continue to return the results from the
    previous template until the result expires.

    ## Args:

    - id (int): Primary key id for the query interface
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - query_in (schemas.QueryUpdate): Object specifying the fields to
    update for the query interface.
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 400 - When the user attempting to access the
    endpoint is not a superuser.
    - HTTPException: 404 - When attempting to update a query interface
    that doesn't exist.

    ## Returns:

    - models.QueryInterface: The updated query interface.
    """
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
    """# Delete a query interface

    Delete a query interface. The interface will no longer be available
    to return results.

    ## Args:

    - id (int): Primary key id for the query interface
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 400 - When the user attempting to access the
    endpoint is not a superuser.
    - HTTPException: 404 - When attempting to delete a query interface
    that doesn't exist.

    ## Returns:

    - models.QueryInterface: The deleted query interface.
    """
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
    """# Run a query and return the result

    Running the query always returns a list, even if there's only one
    result. Each time the query is run, if it's been longer than the
    query interface's refresh_interval since the last time it was run,
    return a cached result. The schema of the result will match the
    schema specified by the query template 'select' field. A user
    accessing this endpoint must either have read permissions on the
    query interface or be a superuser.

    ## Args:

    - resource_id (int): Primary key ID for the query interface.
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - page (int, optional): The page of results to return. Defaults
    to 0.
    - page_size (int, optional): The size of each page of results.
    Defaults to 25.
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_superuser).

    ## Raises:

    - HTTPException: 404 - When attempting to run a query in a query
    interface that doesn't exist.
    - HTTPException: 403 - When the user doesn't have read permissions
    on the query interface.

    # Returns:

    - List[Dict[str, Any]]: List of query results, schema dependent on
    the query template 'select' clause.
    """
    query = crud.query.get(db=db, id=resource_id)
    if not query:
        raise HTTPException(status_code=404, detail="Cannot find query.")
    query_result = crud.query.run_query(
        db=db, id=resource_id, page=page, page_size=page_size
    )
    return jsonable_encoder(query_result)
