from typing import Optional, List

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.expression import literal_column


from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase, GenericModelList, parse_sort_col
from app.models.permission import Permission
from app.models.user import User
from app.models.user_group import UserGroup, UserGroupPermissionRel, UserGroupUserRel
from app.schemas.permission import PermissionTypeEnum
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_user_groups(self, db: Session, *, user: User) -> List[UserGroup]:
        return user.user_groups

    def get_multi_in_group(
        self,
        db: Session,
        *,
        user_group_id: int,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = "",
        sort_desc: Optional[bool] = None,
    ) -> GenericModelList:
        base_query = (
            db.query(User)
            .join(User.user_groups)
            .filter(UserGroup.id == user_group_id)
            .order_by(parse_sort_col(self.model, sort_by=sort_by, sort_desc=sort_desc))
        )
        total_records = base_query.count()
        records = base_query.offset(skip).limit(limit).all()
        return GenericModelList[User](total_records=total_records, records=records)

    def get_multi_not_in_group(
        self,
        db: Session,
        *,
        user_group_id: int,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = "",
        sort_desc: Optional[bool] = None,
    ) -> GenericModelList:
        filter_expression = UserGroup.id != user_group_id
        base_query = (
            db.query(User)
            .outerjoin(User.user_groups)
            .filter(or_(UserGroup.id != user_group_id, UserGroup.id == None))
            .order_by(parse_sort_col(self.model, sort_by=sort_by, sort_desc=sort_desc))
        )
        total_records = base_query.count()
        records = base_query.offset(skip).limit(limit).all()
        return GenericModelList[User](total_records=total_records, records=records)

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

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
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
        self,
        db,
        user: User,
        resource_type: str,
        resource_id: int,
        permission_type: PermissionTypeEnum,
    ) -> bool:
        query = (
            db.query(Permission)
            .join(UserGroupPermissionRel)
            .join(UserGroup)
            .join(UserGroupUserRel)
            .join(User)
            .filter(
                and_(
                    User.id == user.id,
                    Permission.permission_type == permission_type,
                    literal_column("permission.resource_type") == resource_type,
                    literal_column("permission.resource_id") == resource_id,
                )
            )
            .add_columns(UserGroupPermissionRel.enabled)
        )

        result = query.first()
        if result:
            return result.enabled
        return False


user = CRUDUser(User)
