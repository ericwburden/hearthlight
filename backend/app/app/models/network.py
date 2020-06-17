from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Network(Base):
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_by_user = relationship("User", back_populates="networks_created")
    updated_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    updated_by_user = relationship("User", back_populates="networks_updated")
    is_active = Column(Boolean, default=True)