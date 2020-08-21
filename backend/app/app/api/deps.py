from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="The user is not a superuser")
    return current_user


class UserPermissionValidator:
    """
    Provides permission validation for access to resources, based on
    the type of resource and the desired permission. Permissions work
    according to the following rules:

    ## Nodes

    - **create**: Attempting to create a new node requires create
    permissions on the parent node.
    - **read**: Attempting to fetch an existing node or list of nodes
    requires read permission on each node being fetched.
    - **update**: Attempting to update a node requires update
    permissions on the node itself.
    - **delete**: Attempting to delete a node requires delete
    permission on the node itself.

    ## User Groups

    - **create**: Attempting to create a new user group requires create
    permission on the parent node.
    - **read**: Attempting to fetch an existing user group or list of
    user groups requires read permission on each user group being
    fetched.
    - **update**: Attempted to update a user group requires update
    permission on the user group.
    - **delete**: Attempting to delete a user group requires
    delete permission on the user group.

    """

    def __init__(
        self,
        resource_type: schemas.ResourceTypeEnum,
        permission_type: schemas.PermissionTypeEnum,
    ):
        self.resource_type = resource_type
        self.permission_type = permission_type

    def __call__(
        self,
        resource_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
    ):
        if current_user.is_superuser:
            return current_user

        user_has_permission = self.check_permission(resource_id, db, current_user)
        if not user_has_permission:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"User ID {current_user.id} does not have "
                    f"{self.permission_type.value} permissions for "
                    f"{self.resource_type.value} ID {resource_id}"
                ),
            )
        return current_user

    def check_permission(
        self, resource_id: int, db: Session, current_user: models.User
    ):
        return crud.user.has_permission(
            db,
            user=current_user,
            resource_type=self.resource_type,
            resource_id=resource_id,
            permission_type=self.permission_type,
        )
