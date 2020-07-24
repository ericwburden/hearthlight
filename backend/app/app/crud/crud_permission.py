from typing import List, Union, Dict, Any

from fastapi.encoders import jsonable_encoder
from psycopg2.errors import UniqueViolation
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased, with_polymorphic
from sqlalchemy.sql.expression import literal, literal_column

from app.crud.base import CRUDBase
from app.models.user import User
from app.models.permission import Permission, NodePermission
from app.schemas.permission import PermissionCreate, PermissionUpdate, ResourceTypeEnum


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

    def update(
        self,
        db: Session,
        *,
        db_obj: Union[Permission, NodePermission],
        obj_in: Union[PermissionUpdate, Dict[str, Any]]
    ) -> Permission:
        # The default `jsonable_encoder` fails on derived classes. This seems to
        # be related to lazy loading of the class attributes. When `jsonable_encoder`
        # is called on an instance of a db object from a derived class (convoluted,
        # I know), the actual values aren't loaded yet, so obj_data is an empty
        # dictionary
        obj_data = {
            col.name: getattr(db_obj, col.name) for col in db_obj.__table__.columns
        }
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


permission = CRUDPermission(Permission)
node_permission = CRUDPermission(NodePermission)
