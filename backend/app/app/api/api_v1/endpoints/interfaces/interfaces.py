from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.crud.base import GenericModelList

router = APIRouter()


@router.get("/", response_model=GenericModelList[schemas.Interface])
def read_interfaces(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = "",
    sort_desc: Optional[bool] = None,
    name: Optional[str] = None,
    interface_type: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> GenericModelList[schemas.Interface]:
    """# Read a list of interfaces

    Returns interfaces, the first 100 records in descending primary
    key order by default

    ## Args:

    - db (Session, optional): SQLAlchemy Session, injected. Defaults
    to Depends(deps.get_db).
    - skip (int, optional): Number of records to skip. Defaults to 0.
    - limit (int, optional): Number of records to retrieve. Defaults
    to 100.
    - sort_by (str, optional): Name of a column to sort by.
    - sort_desc (bool, optional): Should the column be sorted
    descending (true) or ascending (false).
    - name (str, optional): Filter the results by interface name, via
    name ILIKE "%name%"
    - interface_type (str, optional): Filter the results by interface
    type, via interface_type ILIKE "%interface_type%"
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_user).

    ## Returns:

    - GenericModelList[schemas.Node]: Object containing a count of
    returned records and the records returned.
    """

    search = {
        k: v for k, v in {"name": name, "interface_type": interface_type}.items() if v
    }
    interfaces = crud.interface.get_multi(
        db,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_desc=sort_desc,
        search=search,
    )
    return interfaces
