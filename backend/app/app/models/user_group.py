from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base, Default

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class UserGroupUser(Base, Default):
    user_group_id = Column(Integer, ForeignKey('user_group.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

# user_group_user = Table(
#     'user_group_user',
#     Base.metadata,
#     Column('user_group_id', Integer, ForeignKey('user_group.id')),
#     Column('user_id', Integer, ForeignKey('user.id'))
# )


class UserGroup(Base, Default):
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("node.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    created_by_id = Column(
        Integer,
        ForeignKey("user.id", name=f"fk_user_group_created_by_id", use_alter=True),
        nullable=False,
    )
    created_by_user = relationship(
        "User", back_populates="user_groups_created", foreign_keys=[created_by_id]
    )
    updated_by_id = Column(
        Integer,
        ForeignKey("user.id", name=f"fk_user_group_updated_by_id", use_alter=True),
        nullable=False,
    )
    updated_by_user = relationship(
        "User", back_populates="user_groups_updated", foreign_keys=[updated_by_id]
    )
    name = Column(String(256), nullable=False, unique=True)
    
    users = relationship("User", secondary=lambda: UserGroupUser.__table__, backref="user_groups")
