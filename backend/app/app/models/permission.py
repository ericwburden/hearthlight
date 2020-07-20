from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, String, Table
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401

class Permission(Base):
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String(256), nullable=False)
    permission_type = Column(String(256), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity':'permission',
        'polymorphic_on':resource_type,
        'with_polymorphic':'*'
    }


class NodePermission(Permission):
    resource_id = Column(Integer, ForeignKey('node.id'), index=True)

    __mapper_args__ = {
        'polymorphic_identity':'node',
    }
