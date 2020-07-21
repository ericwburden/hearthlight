from typing import Any, Dict, Optional, Union, List

from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import literal_column

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.node import Node
from app.models.permission import Permission
from app.models.user import User
from app.models.user_group import UserGroup, UserGroupPermission, UserGroupUser
from app.schemas.permission import PermissionTypeEnum
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_user_groups(self, db: Session, *, user: User) -> List[UserGroup]:
        return user.user_groups

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser

    def has_permission(
        self, db, user: User, resource: Union[Node], permission_type: PermissionTypeEnum
    ) -> bool:
        query = (
            db.query(Permission)
            .join(UserGroupPermission)
            .join(UserGroup)
            .join(UserGroupUser)
            .join(User)
            .filter(
                and_(
                    User.id == user.id,
                    Permission.permission_type == permission_type,
                    literal_column("permission.resource_id") == resource.id,
                )
            )
            .add_columns(UserGroupPermission.enabled)
        )

        result = query.first()
        if result:
            return result.enabled
        return False


user = CRUDUser(User)
