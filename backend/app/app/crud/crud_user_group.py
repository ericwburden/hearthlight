from typing import List, Union, Dict, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql.expression import literal, literal_column

from app.crud.base import CRUDBaseLogging
from app.models.user import User
from app.models.permission import Permission
from app.models.user_group import UserGroup, UserGroupUser, UserGroupPermission
from app.schemas.user_group import UserGroupCreate, UserGroupUpdate


class CRUDUserGroup(CRUDBaseLogging[UserGroup, UserGroupCreate, UserGroupUpdate]):
    def add_user_to_group(self, db: Session, *, user_group: UserGroup, user: User) -> UserGroupUser:
        user_group.users.append(user)
        db.commit()
        q = db.query(UserGroupUser).filter(and_(literal_column('user_group_id')==user_group.id, literal_column('user_id')==user.id))
        return q.first()

    def get_users(self, db: Session, *, user_group: UserGroup) -> List[User]:
        return user_group.users

    def remove_user_from_group(self, db:Session, *, user_group: UserGroup, user: User) -> UserGroup:
        user_group.users.remove(user)
        db.commit()
        return user_group

    def add_permission(self, db: Session, *, user_group: UserGroup, permission: Permission, enabled: bool) -> UserGroupPermission:
        user_group_permission = UserGroupPermission(user_group_id=user_group.id, permission_id=permission.id, enabled=enabled)
        db.add(user_group_permission)
        db.commit()
        db.refresh(user_group_permission)
        return user_group_permission

    def get_permission(self, db:Session, *, user_group: UserGroup, permission_id: int) -> Permission:
        return db.query(Permission).join(UserGroupPermission).join(UserGroup).filter(UserGroup.id==user_group.id).first()


    def delete_permission(self, db: Session, *, user_group: UserGroup, permission: Permission) -> UserGroupPermission:
        user_group_permission = db.query(UserGroupPermission).filter(and_(literal_column('user_group_id')==user_group.id, literal_column('permission_id')==permission.id)).first()
        db.delete(user_group_permission)
        db.commit()
        return user_group_permission

user_group = CRUDUserGroup(UserGroup)
