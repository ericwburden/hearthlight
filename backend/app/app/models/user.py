from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .item import Item  # noqa: F401
    from .network import Network


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    items = relationship("Item", back_populates="owner")
    networks_created = relationship(
        "Network",
        back_populates="created_by_user",
        primaryjoin="User.id==Network.created_by_id",
    )
    networks_updated = relationship(
        "Network",
        back_populates="updated_by_user",
        primaryjoin="User.id==Network.updated_by_id",
    )
