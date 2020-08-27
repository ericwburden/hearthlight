from typing import Union, Dict, Any

from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql.expression import literal

from app.crud.base import CRUDBaseLogging, AccessControl
from app.crud.utils import model_encoder
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
        obj_in_data = model_encoder(obj_in)
        obj_in_data["depth"] = 0
        if obj_in_data["parent_id"]:
            parent = self.get(db, obj_in_data["parent_id"])
            obj_in_data["depth"] = parent.depth + 1
        return super().create(db, obj_in=obj_in_data, created_by_id=created_by_id)

    def update(
        self,
        db: Session,
        *,
        db_obj: Node,
        obj_in: NodeUpdate,
        updated_by_id: int
    ) -> Node:
        """Update a node

        Modify the updated node information with the correct depth
        value before passing it up to the CRUDBaseLogging update method

        Args:
            db (Session): SQLAlchemy Session
            db_obj (Node): Reference database object to be updated
            obj_in (NodeUpdate): Update schema
            updated_by_id (int): User id for the user conducting the 
            update operation

        Returns:
            Node: The updated Node
        """

        # If attempting to update the node's parent_id, set the new
        # node depth
        if db_obj.parent_id != obj_in.parent_id:
            parent = self.get(db, obj_in.parent_id)
            obj_in.depth = parent.depth + 1
        return super().update(
            db, db_obj=db_obj, obj_in=obj_in, updated_by_id=updated_by_id
        )

    def get_children(self, db: Session, *, id: int):
        node_ids = self.child_node_ids(db, id=id)
        return db.query(self.model).filter(self.model.id.in_(node_ids)).all()

    def get_child_permissions(self, db: Session, *, id: int):
        node_ids = self.child_node_ids(db, id=id)
        return (
            db.query(NodePermission)
            .filter(NodePermission.resource_id.in_(node_ids))
            .all()
        )


node = CRUDNode(Node, NodePermission)
