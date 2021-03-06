from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Query, Session, aliased
from sqlalchemy.sql.expression import literal, literal_column
from sqlalchemy.sql.selectable import CTE

from app.crud.base import (
    CRUDBaseLogging,
    AccessControl,
    GenericModelList,
    node_tree_ids,
)
from app.models import Interface, Node, NodePermission, UserGroup
from app.schemas import NodeCreate, NodeUpdate, NodeChild


# --------------------------------------------------------------------------------------
# region | Support functions for CRUDNode.get_node_children() --------------------------
# --------------------------------------------------------------------------------------


def user_group_children_cte(db: Session) -> CTE:
    return (
        db.query(
            Node.id.label("node_id"),
            literal("user_group").label("child_type"),
            UserGroup.id.label("child_id"),
            UserGroup.name.label("child_name"),
        )
        .join(UserGroup)
        .cte(name="user_group_children")
    )


def interface_children_cte(db: Session) -> CTE:
    return (
        db.query(
            Node.id.label("node_id"),
            literal("interface").label("child_type"),
            Interface.id.label("child_id"),
            Interface.name.label("child_name"),
        )
        .join(Interface, Node.interfaces)
        .cte(name="interface_children")
    )


def node_children_cte(db: Session) -> CTE:
    child_node = aliased(Node)
    return (
        db.query(
            Node.id.label("node_id"),
            literal("node").label("child_type"),
            child_node.id.label("child_id"),
            child_node.name.label("child_name"),
        )
        .join(child_node, Node.id == child_node.parent_id)
        .cte(name="node_children")
    )


def all_children(db: Session) -> Query:
    child_node = aliased(Node)
    node_children = db.query(
        Node.id.label("node_id"),
        literal("node").label("child_type"),
        child_node.id.label("child_id"),
        child_node.name.label("child_name"),
    ).join(child_node, Node.id == child_node.parent_id)
    user_group_children = db.query(user_group_children_cte(db))
    interface_children = db.query(interface_children_cte(db))
    return node_children.union(user_group_children, interface_children)


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Node CRUD class -------------------------------------------------------------
# --------------------------------------------------------------------------------------


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
        obj_in_data = obj_in.dict()
        if obj_in.parent_id:
            parent = self.get(db, obj_in.parent_id)
            obj_in_data["depth"] = parent.depth + 1
        return super().update(
            db, db_obj=db_obj, obj_in=obj_in, updated_by_id=updated_by_id
        )

    def get_by_name(self, db: Session, name: str) -> Optional[Node]:
        """Feth a node by name

        Node names are unique

        Args:
            db (Session): SQLAlchemy Session
            name (str): Node name to search for

        Returns:
            Optional[Node]: The found node, or None if no node with the
            given name
        """
        return db.query(self.model).filter(self.model.name == name).first()

    def get_types(self, db: Session) -> List[str]:
        """Fetch a list of node types

        Except for 'network'

        Args:
            db (Session): SQLAlchemy Session

        Returns:
            List[str]: List of node types in the database
        """
        unique_types = db.query(self.model.node_type).distinct().all()
        return [ut.node_type for ut in unique_types if ut.node_type != "network"]

    def get_multi_networks(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> GenericModelList:
        base_query = (
            db.query(self.model)
            .order_by(self.model.id.desc())
            .filter(self.model.parent_id == None)
        )
        total_records = base_query.count()
        records = base_query.offset(skip).limit(limit).all()
        return GenericModelList[self.model](
            total_records=total_records, records=records
        )

    def get_child_nodes(self, db: Session, *, id: int) -> List[Node]:
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

    def get_node_children(self, db: Session, *, id: int) -> List[NodeChild]:
        """Fetch a list of node children, all types

        Args:
            db (Session): SQLAlchemy Session
            id (int): Primary key ID for the node

        Returns:
            List[NodeChild]: Listing of node child records
        """
        node_child_records = (
            all_children(db).filter(literal_column("node_id") == id).all()
        )
        return [
            NodeChild(**child_record._asdict()) for child_record in node_child_records
        ]

    def add_interface(self, db: Session, *, node: Node, interface: Interface) -> Node:
        """Attach an interface to a node

        Args:
            db (Session): SQLAlchemy Session
            node (Node): The node to attach the interface to
            interface (Interface): The interface to attach to the node

        Returns:
            Node: The node after attaching the interface
        """
        node.interfaces.append(interface)
        db.commit()
        db.refresh(node)
        return node

    def remove_interface(
        self, db: Session, *, node: Node, interface: Interface
    ) -> Node:
        """Detach an interface from a node

        Args:
            db (Session): SQLAlchemy Session
            node (Node): The node to detach the interface from
            interface (Interface): The interface to detach from the node

        Returns:
            Node: The node after detaching the interface
        """
        node.interfaces.remove(interface)
        db.commit()
        db.refresh(node)
        return node


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------


node = CRUDNode(Node, NodePermission)
