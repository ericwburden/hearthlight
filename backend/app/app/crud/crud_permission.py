from typing import List, Union, Dict, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_
from sqlalchemy.orm import Session, aliased, with_polymorphic
from sqlalchemy.sql.expression import literal, literal_column

from app.crud.base import CRUDBase
from app.models.user import User
from app.models.permission import Permission, NodePermission
from app.schemas.permission import PermissionCreate, PermissionUpdate, ResourceTypeEnum




class CRUDPermission(CRUDBase[Union[Permission,NodePermission], PermissionCreate, PermissionUpdate]):
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
        obj_data = {col.name: getattr(db_obj, col.name) for col in db_obj.__table__.columns}
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
