from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .item import Item  # noqa: F401
    from .node import Node


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    items = relationship("Item", back_populates="owner")
    nodes_created = relationship(
        "Node",
        back_populates="created_by_user",
        primaryjoin="User.id==Node.created_by_id",
    )
    nodes_updated = relationship(
        "Node",
        back_populates="updated_by_user",
        primaryjoin="User.id==Node.updated_by_id",
    )
