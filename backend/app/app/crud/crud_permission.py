from typing import Union, List

from psycopg2.errors import UniqueViolation
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import literal_column

from app.crud.base import CRUDBase
from app.models import Permission, NodePermission, UserGroupPermissionRel
from app.schemas.permission import PermissionCreate, PermissionUpdate


class CRUDPermission(
    CRUDBase[Union[Permission, NodePermission], PermissionCreate, PermissionUpdate]
):
    def create(self, db: Session, *, obj_in: PermissionCreate) -> Permission:
        try:
            return super().create(db, obj_in=obj_in)
        except IntegrityError as e:
            # There is a unique constraint on the Permission table to unique
            # combinations of resource_id and permission_type. If the permission
            # already exists in the database, just return the existing permission
            # Otherwise, pass the exception on
            db.rollback()
            if isinstance(e.orig, UniqueViolation):
                query = db.query(Permission).filter(
                    and_(
                        literal_column("resource_id") == obj_in.resource_id,
                        literal_column("permission_type") == obj_in.permission_type,
                    )
                )
                return query.first()
            raise e

    def update(self, *args, **kwargs) -> None:
        """This function is disabled for Permissions
        """
        pass

    def grant(
        self, db: Session, *, user_group_id: int, permission_id: int
    ) -> UserGroupPermissionRel:
        user_group_permission = UserGroupPermissionRel(
            user_group_id=user_group_id, permission_id=permission_id
        )
        user_group_permission.enabled = True
        db.add(user_group_permission)
        db.commit()
        db.refresh(user_group_permission)
        return user_group_permission

    # TODO: Need a CRUD tests for this function, there's a known issue with
    # attempting to grant permissions that already exist.
    def grant_multiple(
        self, db: Session, *, user_group_id: int, permission_ids: List[int]
    ) -> int:
        user_group_permissions = [
            UserGroupPermissionRel(
                user_group_id=user_group_id, permission_id=pid, enabled=True
            )
            for pid in permission_ids
        ]
        result = db.bulk_save_objects(user_group_permissions)
        breakpoint()
        db.commit()
        return len(permission_ids)

    def revoke(
        self, db: Session, *, user_group_id: int, permission_id: int
    ) -> UserGroupPermissionRel:
        user_group_permission = (
            db.query(UserGroupPermissionRel)
            .filter(
                UserGroupPermissionRel.user_group_id == user_group_id,
                UserGroupPermissionRel.permission_id == permission_id,
            )
            .one()
        )
        user_group_permission.enabled = False
        db.commit()
        db.refresh(user_group_permission)
        return user_group_permission


permission = CRUDPermission(Permission)
node_permission = CRUDPermission(NodePermission)
