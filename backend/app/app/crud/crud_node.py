from typing import Union, Dict, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql.expression import literal

from app.crud.base import CRUDBaseLogging, AccessControl
from app.models.node import Node
from app.models.permission import NodePermission
from app.schemas.node import NodeCreate, NodeUpdate


class CRUDNode(
    AccessControl[Node, NodePermission], CRUDBaseLogging[Node, NodeCreate, NodeUpdate]
):
    def child_node_ids(self, db: Session, *, id: int):
        rec = db.query(literal(id).label("id")).cte(
            recursive=True, name="recursive_node_children"
        )
        ralias = aliased(rec, name="R")
        lalias = aliased(self.model, name="L")
        rec = rec.union_all(
            db.query(lalias.id).join(ralias, ralias.c.id == lalias.parent_id)
        )
        return db.query(rec).all()

    # Modify create function to ensure validation on node.depth
    def create(self, db: Session, *, obj_in: NodeCreate, created_by_id: int) -> Node:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["depth"] = 0
        if obj_in_data["parent_id"]:
            parent = self.get(db, obj_in_data["parent_id"])
            obj_in_data["depth"] = parent.depth + 1
        return super().create(db, obj_in=obj_in_data, created_by_id=created_by_id)

    # Needed a custom update to ensure validation on node.depth
    def update(
        self,
        db: Session,
        *,
        db_obj: Node,
        obj_in: Union[NodeCreate, Dict[str, Any]],
        updated_by_id: int
    ) -> Node:
        # TODO: Update this like the create method
        obj_data = {
            col.name: getattr(db_obj, col.name) for col in db_obj.__table__.columns
        }
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        if db_obj.parent_id != obj_in.parent_id:
            parent = self.get(db, obj_in.parent_id)
            update_data["depth"] = parent.depth + 1
        update_data["updated_by_id"] = updated_by_id

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_children(self, db: Session, *, id: int):
        node_ids = self.child_node_ids(db, id=id)
        return db.query(self.model).filter(self.model.id.in_(node_ids)).all()

    # def instantiate_permissions(self, db: Session, *, node: Node) -> List[Permission]:
    #     permissions = [
    #         NodePermission(
    #             resource_id=node.id,
    #             resource_type="node",
    #             permission_type=permission_type,
    #         )
    #         for permission_type in list(PermissionTypeEnum)
    #     ]
    #     for permission in permissions:
    #         db.add(permission)
    #     db.commit()
    #     return (
    #         db.query(NodePermission)
    #         .join(Node, NodePermission.resource_id == Node.id)
    #         .filter(Node.id == node.id)
    #         .all()
    #     )

    # def get_permissions(self, db: Session, *, id: int) -> List[Permission]:
    #     return db.query(NodePermission).join(Node).filter(Node.id == id).all()

    # def get_permission(
    #     self, db: Session, *, id: int, permission_type: PermissionTypeEnum
    # ) -> Permission:
    #     query = db.query(NodePermission).filter(
    #         and_(
    #             NodePermission.resource_id == id,
    #             NodePermission.permission_type == permission_type,
    #         )
    #     )
    #     permission = query.first()
    #     if not permission:
    #         msg = (
    #             f"Could not find {permission_type.value} permission "
    #             f"for {self.model.__name__} {id}"
    #         )
    #         raise NoResultFound(msg)
    #     return permission

    def get_child_permissions(self, db: Session, *, id: int):
        node_ids = self.child_node_ids(db, id=id)
        return (
            db.query(NodePermission)
            .filter(NodePermission.resource_id.in_(node_ids))
            .all()
        )


node = CRUDNode(Node, NodePermission)
