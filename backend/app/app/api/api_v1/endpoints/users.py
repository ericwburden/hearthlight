from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.crud.base import GenericModelList
from app.utils import send_new_account_email
from app.schemas.permission import PermissionTypeEnum, ResourceTypeEnum

user_group_create_validator = deps.UserPermissionValidator(
    resource_type=ResourceTypeEnum.user_group, permission_type=PermissionTypeEnum.create
)

router = APIRouter()


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> models.User:
    """# Create a new user

    Create a new user in the database. Users are unique by email
    address (username). In order to create a new user, the username must
    be unique. Additionally, if the user performing the operation is not
    a superuser, a user group must be provided as a home for the new
    user. The indicated user group must exist in the database and the
    normal user must have create permissions for the user group
    indicated.

    ## Args:

    - user_in (schemas.UserCreate): Schema for creating a new user
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_user).

    ## Raises:

    - HTTPException: 400 - When attempting to create a user with a
    username that already exists.
    - HTTPException: 403 - When a normal user attempts to create a user
    without providing a user group id.
    - HTTPException: 404 - When a normal user provides a user group id
    for a user group that doesn't exist.
    - HTTPException: 403 - When a normal user attempts to create a user
    in a user group without create permissions on the user group.

    Returns:

    - models.User: The created user
    """
    user_group = None
    if not current_user.is_superuser:
        if not user_in.user_group_id:
            raise HTTPException(
                status_code=403, detail="Non-superuser must provide a user group."
            )
        user_group = crud.user_group.get(db, user_in.user_group_id)
        if not user_group:
            raise HTTPException(status_code=404, detail="Can not find user group.")
        user_group_create_validator(
            resource_id=user_in.user_group_id, db=db, current_user=current_user
        )

    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    user = crud.user.create(db, obj_in=user_in)
    if user_group:
        crud.user_group.add_user(db, user_group=user_group, user_id=user.id)

    if settings.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> models.User:
    """# Get current user model

    Retrieving a user from the database requires the user performing
    the fetch to either be the user being fetched or a superuser. This
    endpoint only fetches the current user's model.

    ## Args:

    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_user).

    ## Returns:

    - User: The database model for the current user
    """

    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> models.User:
    """# Get current user model

    Retrieving a user from the database requires the user performing
    the fetch to either be the user being fetched or a superuser. This
    endpoint can be used to fetch any user by id, with appropriate
    access.

    ## Args:

    - user_id (int): Primary key id for the user being retrieved.
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_user).

    ## Returns:

    - User: The database model for the current user
    """

    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.get("/", response_model=GenericModelList[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = "",
    sort_desc: Optional[bool] = None,
    full_name: Optional[str] = None,
    email: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> GenericModelList[schemas.User]:
    """# Fetch a list of users

    This endpoint fetches all users in the database. Only available to
    the superuser.

    ## Args:

    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - skip (int, optional): Number of records to skip. Defaults to 0.
    - limit (int, optional): Number of record to retrieve. Defaults to
    100.
    - sort_by (str, optional): Name of a column to sort by.
    - sort_desc (bool, optional): Should the column be sorted
    descending (true) or ascending (false).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_user).

    ## Returns:

    - GenericModelList[schemas.Node]: Object containing a count of
    returned records and the records returned.
    """
    search = {k: v for k, v in {"full_name": full_name, "email": email}.items() if v}
    users = crud.user.get_multi(
        db,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_desc=sort_desc,
        search=search,
    )
    return users


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> models.User:
    """# Update self (user)

    A normal user may update their own user model in a limited way,
    by modifying password, full name, or email address. The new email
    address needs to be unique, the same as when creating a new user.

    ## Args:

    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - password (str, optional): New password. Defaults to Body(None).
    - full_name (str, optional): New full name. Defaults to Body(None).
    - email (EmailStr, optional): New email address. Defaults to
    Body(None).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_user).

    ## Raises:

    - HTTPException: 400 - When attempting to update a user's email
    to an email address that is already in the database.

    ## Returns:

    - User: The updated user model
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if email is not None:
        in_database = crud.user.get_by_email(db, email=email)
        if in_database:
            raise HTTPException(
                status_code=400,
                detail="A user with this username already exists in the system.",
            )
        user_in.email = email
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> models.User:
    """# Update a user by ID

    A superuser may update another user model, identified by primary
    key ID. The normal stricture on unique email address still applies.

    ## Args:

    - user_id (int): Primary key ID for the user to update
    - user_in (schemas.UserUpdate): User update schema
    - db (Session, optional): SQLAlchemy Session. Defaults to
    Depends(deps.get_db).
    - current_user (models.User, optional): User object for the user
    accessing the endpoint. Defaults to
    Depends(deps.get_current_active_user).

    ## Raises:

    - HTTPException: 404 - When the user identified by user_id doesn't
    exist in the database.
    - HTTPException: 400 - When attempting to update the user's email
    address to an email address that is already in the system.

    ## Returns:

    - models.User: The updated User model
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Can not find user.")
    if getattr(user_in, "email", None):
        in_database = crud.user.get_by_email(db, email=user_in.email)
        if in_database:
            raise HTTPException(
                status_code=400,
                detail="A user with this username already exists in the system.",
            )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user
