from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base, Default

if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .permission import Permission # noqa


class UserGroupUser(Base, Default):
    user_group_id = Column(Integer, ForeignKey('user_group.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)


class UserGroupPermission(Base, Default):
    user_group_id = Column(Integer, ForeignKey('user_group.id'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permission.id'), primary_key=True)
    enabled = Column(Boolean, default=False)

    user_group = relationship("UserGroup", backref="permissions")
    permission = relationship("Permission", backref="user_groups")


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