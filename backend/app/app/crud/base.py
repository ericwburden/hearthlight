from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session, aliased
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_, literal

from app.db.base_class import Base
from app.models import (
    Node,
    User,
    UserGroup,
    UserGroupPermissionRel,
    UserGroupUserRel,
    Permission,
)
from app.schemas import PermissionTypeEnum

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

    def create(
        self, db: Session, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = jsonable_encoder(obj_in)
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
        obj_data = jsonable_encoder(db_obj)
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
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        setattr(db_obj, "created_by_id", created_by_id)
        setattr(db_obj, "updated_by_id", created_by_id)
        return super().create(db, obj_in=db_obj)

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        updated_by_id: int,
    ) -> ModelType:
        obj_data = {
            col.name: getattr(db_obj, col.name) for col in db_obj.__table__.columns
        }
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        update_data["updated_by_id"] = updated_by_id
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class AccessControl(Generic[ModelType, PermissionType]):
    def __init__(self, model: Type[ModelType], permission_model: Type[PermissionType]):
        self.permission_model = permission_model
        super().__init__(model)

    def create(self, db: Session, *args, **kwargs) -> ModelType:
        created_obj = super().create(db, *args, **kwargs)
        permissions = [
            self.permission_model(
                resource_id=created_obj.id,
                resource_type=self.model.__tablename__,
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
        return (
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
            .all()
        )

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

    def get_node_descendants(self, db: Session, *, node_id: int) -> List[ModelType]:
        """Fetch all resources of the same ModelType that are in the
        list of descendants from the indicated root node, meaning, the
        resource is attached to a node descended from the root node.

        Args:
            db (Session): SQLAlchemy Session
            node_id (int): Primary key ID for the root node

        Returns:
            List[ModelType]: List of databse objects
        """
        node_ids = node_tree_ids(db, node_id=node_id)
        return db.query(self.model).filter(self.model.node_id.in_(node_ids)).all()

    def is_descended_from(self, db: Session, *, node_id: int) -> bool:
        """Determine whether the resource is in the descendant tree for
        a node indicated by node_id. Must be implemented on each
        subclass of AccessControl

        Args:
            db (Session): SQLAlchemy Session
            node_id (int): Primary key id for root node

        Returns:
            bool: Is the resource descended from the root node?
        """
        raise NotImplementedError
