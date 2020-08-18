from typing import TYPE_CHECKING

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    DateTime,
    Boolean,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .user_group import UserGroupPermissionRel  # noqa


class Permission(Base):
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String(256), nullable=False)
    permission_type = Column(String(256), nullable=False)

    user_groups = relationship("UserGroupPermissionRel", cascade="all, delete")

    __mapper_args__ = {
        "polymorphic_identity": "permission",
        "polymorphic_on": resource_type,
        "with_polymorphic": "*",
    }


class NodePermission(Permission):
    @declared_attr
    def resource_id(cls): # noqa
        return Permission.__table__.c.get('resource_id', Column(Integer, index=True))

    __mapper_args__ = {
        "polymorphic_identity": "node",
    }


class UserGroupPermission(Permission):
    @declared_attr
    def resource_id(cls): # noqa
        return Permission.__table__.c.get('resource_id', Column(Integer, index=True))

    __mapper_args__ = {
        "polymorphic_identity": "user_group",
    }


uc = UniqueConstraint("resource_id", "permission_type", name="resource_permission_uc")
Permission.__table__.append_constraint(uc)
