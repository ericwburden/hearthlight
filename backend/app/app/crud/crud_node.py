from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBaseLogging, AccessControl, node_tree_ids
from app.models.node import Node
from app.models.permission import NodePermission
from app.schemas.node import NodeCreate, NodeUpdate


class CRUDNode(
    AccessControl[Node, NodePermission], CRUDBaseLogging[Node, NodeCreate, NodeUpdate]
):

    # Modify create function to ensure validation on node.depth
    def create(self, db: Session, *, obj_in: NodeCreate, created_by_id: int) -> Node:
        """Create a node

        Sets the new node's depth before passing the request to
        CRUDBaseLogging.create()

        Args:
            db (Session): SQLAlchemy Session
            obj_in (NodeCreate): Node create schema
            created_by_id (int): User id for the user creating the node

        Returns:
            Node: the created Node
        """
        depth = 0
        if getattr(obj_in, "parent_id", None):
            parent = self.get(db, obj_in.parent_id)
            depth = parent.depth + 1
        obj_in_data = obj_in.dict(exclude_unset=True)
        obj_in_data["depth"] = depth
        return super().create(db, obj_in=obj_in_data, created_by_id=created_by_id)

    def update(
        self, db: Session, *, db_obj: Node, obj_in: NodeUpdate, updated_by_id: int
    ) -> Node:
        """Update a node

        Modify the updated node information with the correct depth
        value before passing it up to CRUDBaseLogging.update()

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

    def get_children(self, db: Session, *, id: int) -> List[Node]:
        """Fetch all child nodes

        Returns all nodes at or below the target node (indicated by id)
        in the node hierarchy

        Args:
            db (Session): SQLAlchemy Session
            id (int): Primary key id for the root node

        Returns:
            List[Node]: list of Nodes, contains the root node and all
            descendants
        """
        node_ids = node_tree_ids(db, id=id)
        return db.query(self.model).filter(self.model.id.in_(node_ids)).all()


node = CRUDNode(Node, NodePermission)
