from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base, Default

if TYPE_CHECKING:
    from .node import Node  # noqa
    from .user import UserGroup  # noqa


class User(Base, Default):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)

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

    user_groups_created = relationship(
        "UserGroup",
        back_populates="created_by_user",
        primaryjoin="User.id==UserGroup.created_by_id",
    )
    user_groups_updated = relationship(
        "UserGroup",
        back_populates="updated_by_user",
        primaryjoin="User.id==UserGroup.updated_by_id",
    )
