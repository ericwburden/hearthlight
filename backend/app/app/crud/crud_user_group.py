from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session

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
        return db.query(UserGroupUserRel).get((user_group.id, user.id))

    def add_users(
        self, db: Session, *, user_group: UserGroup, user_ids: List[int]
    ) -> List[UserGroupUserRel]:
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        [user_group.users.append(user) for user in users]
        db.commit()
        return (
            db.query(UserGroupUserRel)
            .filter(
                and_(
                    UserGroupUserRel.user_id.in_(user_ids),
                    UserGroupUserRel.user_group_id == user_group.id,
                )
            )
            .all()
        )

    def get_users(self, db: Session, *, user_group: UserGroup) -> List[User]:
        return user_group.users

    def remove_user(
        self, db: Session, *, user_group: UserGroup, user: User
    ) -> User:
        user_group.users.remove(user)
        db.commit()
        return user

    def remove_users(
        self, db: Session, *, user_group: UserGroup, users: List[User]
    ) -> List[User]:
        [user_group.users.remove(user) for user in users]
        db.commit()
        return users

    def permissions_in_user_group(self, db: Session, *, id: int) -> List[Permission]:
        user_group = db.query(UserGroup).get(id)
        return user_group.permissions_in


user_group = CRUDUserGroup(UserGroup, UserGroupPermission)
