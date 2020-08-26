from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import literal_column

from app.crud.base import CRUDBaseLogging, AccessControl
from app.models.user import User
from app.models.permission import Permission, UserGroupPermission
from app.models.user_group import UserGroup, UserGroupUserRel, UserGroupPermissionRel
from app.schemas.user_group import UserGroupCreate, UserGroupUpdate


class CRUDUserGroup(
    AccessControl[UserGroup, UserGroupPermission],
    CRUDBaseLogging[UserGroup, UserGroupCreate, UserGroupUpdate],
):
    def add_user(
        self, db: Session, *, user_group: UserGroup, user_id: int
    ) -> UserGroupUserRel:
        user = db.query(User).get(user_id)
        user_group.users.append(user)
        db.commit()
        q = db.query(UserGroupUserRel).filter(
            and_(
                literal_column("user_group_id") == user_group.id,
                literal_column("user_id") == user_id,
            )
        )
        return q.first()

    def get_users(self, db: Session, *, user_group: UserGroup) -> List[User]:
        return user_group.users

    def remove_user(
        self, db: Session, *, user_group: UserGroup, user: User
    ) -> UserGroup:
        user_group.users.remove(user)
        db.commit()
        return user_group

    def all_permissions_in_user_group(
        self, db: Session, *, user_group_id: int
    ) -> List[Permission]:
        return (
            db.query(Permission)
            .join(UserGroupPermissionRel)
            .join(UserGroup).filter(UserGroup.id == user_group_id)
            .all()
        )


user_group = CRUDUserGroup(UserGroup, UserGroupPermission)
