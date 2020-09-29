from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql.expression import literal
from sqlalchemy.sql.selectable import CTE

from app.crud.base import CRUDBaseLogging, AccessControl, node_tree_ids
from app.models import Interface, Node, NodePermission, UserGroup
from app.schemas import NodeCreate, NodeUpdate, NodeWithChildren


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


def all_children_cte(db: Session) -> CTE:
    node_children = db.query(node_children_cte(db))
    user_group_children = db.query(user_group_children_cte(db))
    interface_children = db.query(interface_children_cte(db))
    return node_children.union(user_group_children, interface_children).cte(
        name="all_node_children"
    )


def node_child_listings_cte(db: Session) -> CTE:
    all_children = all_children_cte(db)
    return (
        db.query(
            Node.id.label("node_id"),
            Node.node_type,
            Node.name.label("node_name"),
            all_children.c.node_children_child_type.label("child_type"),
            func.array_agg(
                func.json_build_object(
                    "child_id",
                    all_children.c.node_children_child_id,
                    "child_name",
                    all_children.c.node_children_child_name,
                )
            ).label("children"),
        )
        .join(all_children, Node.id == all_children.c.node_children_node_id)
        .group_by(
            Node.id,
            Node.node_type,
            Node.name,
            all_children.c.node_children_child_type,
        )
        .order_by(Node.id)
        .cte(name="node_child_listings")
    )


def nodes_with_children_cte(db: Session) -> CTE:
    node_child_listings = node_child_listings_cte(db)
    return (
        db.query(
            node_child_listings.c.node_id,
            node_child_listings.c.node_type,
            node_child_listings.c.node_name,
            func.array_agg(
                func.json_build_object(
                    "child_type",
                    node_child_listings.c.child_type,
                    "children",
                    node_child_listings.c.children,
                )
            ).label("child_lists"),
        )
        .group_by(
            node_child_listings.c.node_id,
            node_child_listings.c.node_type,
            node_child_listings.c.node_name,
        )
        .order_by(node_child_listings.c.node_id)
        .cte(name="nodes_with_children")
    )


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
        if db_obj.parent_id != obj_in.parent_id:
            parent = self.get(db, obj_in.parent_id)
            obj_in.depth = parent.depth + 1
        return super().update(
            db, db_obj=db_obj, obj_in=obj_in, updated_by_id=updated_by_id
        )

    def get_multi_networks(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Node]:
        return (
            db.query(self.model)
            .filter(self.model.node_type == "network")
            .order_by(self.model.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
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

    def get_node_children(self, db: Session, *, id: int) -> NodeWithChildren:
        """Fetch an object describing a node's direct children

        Args:
            db (Session): SQLAlchemy Session
            id (int): Primary key ID of the Node

        Returns:
            NodeWithChildren: The resulting object listing the children
            associated with the indicated node
        """
        nodes_with_children = nodes_with_children_cte(db)
        node_with_children = (
            db.query(nodes_with_children)
            .filter(nodes_with_children.c.node_id == id)
            .first()
        )
        return NodeWithChildren(**node_with_children._asdict())

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
