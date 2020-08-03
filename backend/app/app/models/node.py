from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from app.db.base_class import Base, Default

if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .permission import NodePermission  # noqa


class Node(Base, Default):
    """Class representing Node objects
    
    Nodes represent the basic organizational structure of Hearthlight. All nodes
    are represented in the node table and are organized into a tree-like structure 
    through recursive association by the parent_id attribute, which represents the
    node id of the node's 'parent'. This is a flexible structure which allows for 
    arbitrarily complex organizational structures. All nodes have a parent, with the 
    exception of 'network' nodes, which represent the root of each organizational
    structure. While 'network' is a reserved node_type, any other name can be given to 
    a node to identify the node's purpose in the hierarchy. For example, node types 
    could form the following hierarchy: network(1) > organization(n) > division(n) >
    department(n) > program(n) > team(n). The node table contains the following
    fields:

    - id: primary key
    - parent_id: primary key for the node's parent node
    - created_at: timestamp for creation datetime
    - updated_at: timestamp for update datetime
    - created_by_id: User id for the user who created the node record
    - updated_by_id: User id for the user who last updated the node record
    - depth: integer indicating the number of parents this node has
    - node_type: string indicating the type of node, not constrained to a list
    - name: string representing the name for this node
    - is_active: indicates whether the node is active, which impacts operations on the
    node, such as creating child nodes

    Nodes have relationships with the following object types:

    - Other nodes (parent, children)
    - Users (created_by, updated_by)
    - User Groups (user_groups)
    - Permissions (permissions)
    """

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("node.id"), index=True)
    children = relationship("Node")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    created_by_id = Column(
        Integer,
        ForeignKey("user.id", name=f"fk_node_created_by_id", use_alter=True),
        nullable=False,
    )
    created_by_user = relationship(
        "User", back_populates="nodes_created", foreign_keys=[created_by_id]
    )
    updated_by_id = Column(
        Integer,
        ForeignKey("user.id", name=f"fk_node_updated_by_id", use_alter=True),
        nullable=False,
    )
    updated_by_user = relationship(
        "User", back_populates="nodes_updated", foreign_keys=[updated_by_id]
    )
    depth = Column(Integer, nullable=False)
    node_type = Column(String(64), nullable=False)
    name = Column(String(256), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)

    user_groups = relationship("UserGroup", cascade="all, delete")
    permissions = relationship("NodePermission", backref="node")
