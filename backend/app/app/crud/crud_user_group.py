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
    def get_multi_with_permissions(
        self, db: Session, *, user: User, skip: int = 0, limit: int = 100
    ) -> List[UserGroup]:

        # Need to alias the first instance of UserGroup since it's in
        # the query twice
        user_group_result = aliased(self.model)
        return (
            db.query(user_group_result)
            .join(
                UserGroupPermission,
                UserGroupPermission.resource_id == user_group_result.id,
            )
            .join(UserGroupPermissionRel)
            .join(UserGroup)
            .join(UserGroupUserRel)
            .join(User)
            .filter(
                and_(
                    User.id == user.id,
                    UserGroupPermission.permission_type == PermissionTypeEnum.read,
                    UserGroupPermissionRel.enabled == True,
                )
            )
            .all()
        )

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

    def add_permission_to_user_group(
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

    def get_all_permissions_in_user_group(
        self, db: Session, *, user_group: UserGroup
    ) -> List[Permission]:
        return db.query(Permission).join(UserGroupPermissionRel).join(UserGroup).all()

    def delete_permission_in_user_group(
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

    # The below functions address permmissions *for* the UserGroup,
    # i.e., user permissions to do CRUD operations on the UserGroup
    # itself

    # TODO: Need to figure out how to make this a mixin
    def instantiate_permissions(
        self, db: Session, *, user_group: UserGroup
    ) -> List[Permission]:
        """Create permissions *for* the UserGroup

        Permissions *for* the UserGroup are permissions to perform CRUD
        operations on the UserGroup, not permissions being related to
        Users

        ## Args:

        - db (Session): SQLAlchemy Session
        - user_group (UserGroup): The UserGroup to create permissions for

        ## Returns:
        
        - List[Permission]: The created Permissions, one each of
        'create', 'read', 'update', and 'delete'
        """

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


user_group = CRUDUserGroup(UserGroup)
