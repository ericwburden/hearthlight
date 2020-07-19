from typing import List, Union, Dict, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql.expression import literal

from app.crud.base import CRUDBaseLogging
from app.models.node import Node
from app.schemas.node import NodeCreate, NodeUpdate


class CRUDNode(CRUDBaseLogging[Node, NodeCreate, NodeUpdate]):
    def create(self, db: Session, *, obj_in: NodeCreate, created_by_id: int) -> Node:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["depth"] = 0
        if obj_in_data["parent_id"]:
            parent = self.get(db, obj_in_data["parent_id"])
            obj_in_data["depth"] = parent.depth + 1
        db_obj = self.model(**obj_in_data, created_by_id=created_by_id, updated_by_id=created_by_id)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Node,
        obj_in: Union[NodeCreate, Dict[str, Any]],
        updated_by_id: int
    ) -> Node:
        obj_data = jsonable_encoder(db_obj)
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
        rec = db.query(literal(id).label("id")).cte(
            recursive=True, name="recursive_node_children"
        )
        ralias = aliased(rec, name="R")
        lalias = aliased(self.model, name="L")
        rec = rec.union_all(
            db.query(lalias.id).join(ralias, ralias.c.id == lalias.parent_id)
        )
        node_ids = db.query(rec).all()
        return db.query(self.model).filter(self.model.id.in_(node_ids)).all()


node = CRUDNode(Node)