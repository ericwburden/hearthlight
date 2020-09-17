from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy.orm import Session, aliased
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_, literal

from app.db.base_class import Base
from app.crud.utils import model_encoder
from app.models import (
    Node,
    User,
    UserGroup,
    UserGroupPermissionRel,
    UserGroupUserRel,
    Permission,
)
from app.schemas import PermissionTypeEnum
from app.models.generic import get_generic_model
from app.schemas.generic import get_generic_schema

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
PermissionType = TypeVar("PermissionType", bound=BaseModel)


def node_tree_ids(db: Session, *, id: int) -> List[int]:
    """Fetch a list of node descendant ids, where the root node
    is the node with the given id.

    Args:
        db (Session): SQLAlchemy Session
        id (int): Primary key ID for the root node

    Returns:
        List[int]: List of node ids
    """
    rec = db.query(literal(id).label("id")).cte(
        recursive=True, name="recursive_node_children"
    )
    ralias = aliased(rec, name="R")
    lalias = aliased(Node, name="L")
    rec = rec.union_all(
        db.query(lalias.id).join(ralias, ralias.c.id == lalias.parent_id)
    )
    query = db.query(rec)
    return [v for v, in query.all()]


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return (
            db.query(self.model)
            .order_by(self.model.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_filtered(self, db: Session, *, ids: List[int]) -> List[ModelType]:
        return db.query(self.model).filter(self.model.id.in_(ids)).all()

    def create(
        self, db: Session, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = model_encoder(obj_in)
        db_obj = self.model(**create_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_data = model_encoder(db_obj, db)
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

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj


class CRUDBaseLogging(CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Extends CRUDBase by adding capture for created_by_id and updated_by_id
    to the create and update methods, respectively.
    """

    def create(
        self, db: Session, *, obj_in: CreateSchemaType, created_by_id: int
    ) -> ModelType:
        obj_in_data = model_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        setattr(db_obj, "created_by_id", created_by_id)
        setattr(db_obj, "updated_by_id", created_by_id)
        return super().create(db, obj_in=db_obj)

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        updated_by_id: int,
    ) -> ModelType:
        obj_in_data = obj_in.dict(exclude_unset=True)
        obj_in_data["updatedy_by_id"] = updated_by_id
        return super().update(db, db_obj=db_obj, obj_in=obj_in_data)


class AccessControl(Generic[ModelType, PermissionType]):
    def __init__(self, model: Type[ModelType], permission_model: Type[PermissionType]):
        self.resource_type = permission_model.__mapper__.polymorphic_identity
        self.permission_model = permission_model
        super().__init__(model)

    def create(self, db: Session, *args, **kwargs) -> ModelType:
        created_obj = super().create(db, *args, **kwargs)
        permissions = [
            self.permission_model(
                resource_id=created_obj.id,
                resource_type=self.resource_type,
                permission_type=permission_type,
            )
            for permission_type in list(PermissionTypeEnum)
        ]
        for permission in permissions:
            db.add(permission)
        db.commit()
        return created_obj

    def get_multi_with_permissions(
        self, db: Session, *, user: User, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        result_model = aliased(self.model)
        query = (
            db.query(result_model)
            .join(
                self.permission_model,
                self.permission_model.resource_id == result_model.id,
            )
            .join(UserGroupPermissionRel)
            .join(UserGroup)
            .join(UserGroupUserRel)
            .join(User)
            .filter(
                and_(
                    User.id == user.id,
                    self.permission_model.permission_type == PermissionTypeEnum.read,
                    UserGroupPermissionRel.enabled == True,  # noqa E712
                )
            )
        )
        return query.all()

    def get_permissions(self, db: Session, *, id: int) -> List[Permission]:
        return (
            db.query(self.permission_model)
            .join(self.model, self.permission_model.resource_id == self.model.id)
            .filter(self.model.id == id)
            .all()
        )

    def get_permission(
        self, db: Session, *, id: int, permission_type: PermissionTypeEnum
    ) -> Permission:
        query = db.query(self.permission_model).filter(
            and_(
                self.permission_model.resource_id == id,
                self.permission_model.permission_type == permission_type,
            )
        )
        permission = query.first()
        if not permission:
            msg = (
                f"Could not find {permission_type.value} permission "
                f"for {self.model.__name__} {id}"
            )
            raise NoResultFound(msg)
        return permission


class CRUDInterfaceBase(CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, id: int, table_name: str):
        self.interface_id = id
        self.model = get_generic_model(table_name)
        self.schema = get_generic_schema(table_name)

    def get_model(self):
        return self.model

    def get_schema(self):
        return self.schema

    def create(self, db: Session, *, obj_in: Dict[str, Any]) -> ModelType:
        # Inject the interface id as a foreign key and validate the
        # structure of the obj_in against the target table model
        new_obj = self.schema(**obj_in, interface_id=self.interface_id)
        return super().create(db, obj_in=new_obj)

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: Dict[str, Any],
    ) -> ModelType:
        # For every table column, take either the existing value or the
        # new value being passed in through 'obj_in'
        check_data = {
            attr: obj_in.get(attr) if obj_in.get(attr) else getattr(db_obj, attr)
            for attr in db_obj.__table__.columns.keys()
        }
        self.schema(**check_data)  # Checks for validation errors
        return super().update(db, db_obj=db_obj, obj_in=obj_in)
