from typing import List, Union, Dict, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql.expression import literal, literal_column

from app.crud.base import CRUDBaseLogging
from app.models.user import User
from app.models.permission import Permission, UserGroupPermission
from app.models.user_group import UserGroup, UserGroupUserRel, UserGroupPermissionRel
from app.schemas.user_group import UserGroupCreate, UserGroupUpdate
from app.schemas.permission import PermissionTypeEnum


class CRUDUserGroup(CRUDBaseLogging[UserGroup, UserGroupCreate, UserGroupUpdate]):
    def add_user_to_group(
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

    def remove_user_from_group(
        self, db: Session, *, user_group: UserGroup, user: User
    ) -> UserGroup:
        user_group.users.remove(user)
        db.commit()
        return user_group

    def add_permission(
        self,
        db: Session,
        *,
        user_group: UserGroup,
        permission: Permission,
        enabled: bool
    ) -> UserGroupPermissionRel:
        user_group_permission = UserGroupPermissionRel(
            user_group_id=user_group.id, permission_id=permission.id, enabled=enabled
        )
        db.add(user_group_permission)
        db.commit()
        db.refresh(user_group_permission)
        return user_group_permission

    # def get_permission(
    #     self, db: Session, *, user_group: UserGroup, permission_id: int
    # ) -> Permission:
    #     return (
    #         db.query(Permission)
    #         .join(UserGroupPermissionRel)
    #         .join(UserGroup)
    #         .filter(UserGroup.id == user_group.id)
    #         .first()
    #     )

    # TODO: Gonna need a cleaner way to differentiate between permissions *in*
    # a UserGroup and permissions *for* a UserGroup. For now, I've commented
    # the previous get_permission() function, which WILL cause problems.
    # Consider moving the permission association CRUD to the crud_permission
    # module
    def get_permission(
        self, db: Session, *, id: int, permission_type: PermissionTypeEnum
    ) -> Permission:
        query = db.query(UserGroupPermission).filter(
            and_(
                UserGroupPermission.resource_id == id,
                UserGroupPermission.permission_type == permission_type,
            )
        )
        return query.first()

    def get_all_permissions(
        self, db: Session, *, user_group: UserGroup
    ) -> List[Permission]:
        return db.query(Permission).join(UserGroupPermissionRel).join(UserGroup).all()

    def delete_permission(
        self, db: Session, *, user_group: UserGroup, permission: Permission
    ) -> UserGroupPermissionRel:
        user_group_permission = (
            db.query(UserGroupPermissionRel)
            .filter(
                and_(
                    literal_column("user_group_id") == user_group.id,
                    literal_column("permission_id") == permission.id,
                )
            )
            .first()
        )
        db.delete(user_group_permission)
        db.commit()
        return user_group_permission

    def grant_permission(
        self, db: Session, *, user_group: UserGroup, permission: Permission
    ) -> UserGroupPermissionRel:
        user_group_permission = (
            db.query(UserGroupPermissionRel)
            .filter(
                and_(
                    literal_column("user_group_id") == user_group.id,
                    literal_column("permission_id") == permission.id,
                )
            )
            .first()
        )
        user_group_permission.enabled = True
        db.add(user_group_permission)
        db.commit()
        db.refresh(user_group_permission)
        return user_group_permission

    def revoke_permission(
        self, db: Session, *, user_group: UserGroup, permission: Permission
    ) -> UserGroupPermissionRel:
        user_group_permission = (
            db.query(UserGroupPermissionRel)
            .filter(
                and_(
                    literal_column("user_group_id") == user_group.id,
                    literal_column("permission_id") == permission.id,
                )
            )
            .first()
        )
        user_group_permission.enabled = False
        db.add(user_group_permission)
        db.commit()
        db.refresh(user_group_permission)
        return user_group_permission

    # TODO: Need to figure out how to make this a mixin
    def instantiate_permissions(
        self, db: Session, *, user_group: UserGroup
    ) -> List[Permission]:
        permissions = [
            UserGroupPermission(
                resource_id=user_group.id,
                resource_type="user_group",
                permission_type=permission_type,
            )
            for permission_type in list(PermissionTypeEnum)
        ]
        for permission in permissions:
            db.add(permission)
        db.commit()
        return (
            db.query(UserGroupPermission)
            .join(UserGroup, UserGroupPermission.resource_id == UserGroup.id)
            .filter(UserGroup.id == user_group.id)
            .all()
        )


user_group = CRUDUserGroup(UserGroup)
