from typing import Union, List

from psycopg2.errors import UniqueViolation
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import literal_column

from app.crud.base import CRUDBase, node_tree_ids
from app.models import Permission, NodePermission, UserGroupPermissionRel, UserGroup
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

    def all_in_database(
        self, db: Session, *, permission_ids: List[int]
    ) -> bool:
        """Asserts whether all the given permission ids are for
        permissions in the database

        Args:
            db (Session): SQLAlchemy Session
            permission_ids (List[int]): Primary key IDs for the
            permissions to check

        Returns:
            bool: Are all the given permissions in the database?
        """
        permissions_in_db = (
            db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        )
        stored_permission_ids = [p.id for p in permissions_in_db]
        return set(permission_ids) == set(stored_permission_ids)

    def in_node_descendants(
        self, db: Session, *, node_id: int, permission: Permission
    ) -> bool:
        """Check if a permission is for a resource descended from the
        given node

        Args:
            db (Session): SQLAlchemy Session
            node_id (int): Primary key ID for the root node to check
            permission (Permission): The permission to check for
            descendant status

        Raises:
            NotImplementedError: Raise for resource types not yet
            implemented

        Returns:
            bool: Is this permission a descendant of the node?
        """
        descendant_ids = node_tree_ids(db, id=node_id)
        if permission.resource_type == 'node':
            return permission.resource_id in descendant_ids

        if permission.resource_type == 'user_group':
            node_id = db.query('UserGroup.node_id').get(permission.resource_id)
            return node_id in descendant_ids

        # If checking for a type not yet covered, raise this error
        msg = f"Descendant check not implemented for {permission.resource_type}."
        raise NotImplementedError(msg)

    def all_node_descendants(
        self, db: Session, *, node_id: int, permissions: List[Permission]
    ) -> bool:
        """Check if all permissions are for a resource descendded
        from the given node

        Args:
            db (Session): SQLAlchemy Session
            node_id (int): Primary key ID for the root node
            permissions (List[Permission]): List of permissions to
            check

        Raises:
            NotImplementedError: Raise for resource_types not yet
            implemented

        Returns:
            bool: Are all the permissions desceneded from the root node?
        """
        implemented_types = ['node', 'user_group']
        for p in permissions:
            if p.resource_type not in implemented_types:
                msg = f"Descendant check not implemented for {p.resource_type}."
                raise NotImplementedError(msg)

        descendant_ids = node_tree_ids(db, id=node_id)
        node_permissions = [p for p in permissions if p.resource_type == 'node']
        for np in node_permissions:
            if np.resource_id not in descendant_ids:
                return False

        user_group_ids = [p.resource_id for p in permissions if p.resource_type == 'user_group']
        user_groups = db.query(UserGroup).filter(UserGroup.id.in_(user_group_ids))
        user_group_node_ids = [ug.node_id for ug in user_groups]
        for ugni in user_group_node_ids:
            if ugni not in descendant_ids:
                return False

        return True


permission = CRUDPermission(Permission)
node_permission = CRUDPermission(NodePermission)
