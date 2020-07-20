from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base, Default

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Node(Base, Default):
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

    user_groups = relationship('UserGroup', backref="node")
