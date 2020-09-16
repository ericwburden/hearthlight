from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON

from app.db.base_class import Base, Default

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Interface(Base, Default):
    """Class representing a definition for an interface

    Interfaces provide I/O for Nodes, and encapsulate functionality such
    as form input, messaging between Nodes, document store, etc. Each
    interface has a set of base functionality defined, but the specific
    data stored for each interface may not be known until run-time (or
    later). In order to accommodate this, the table structure and UI
    structure is stored in the interface table in a JSON
    column. Once the table is created, the table_created column should
    be set to 'True'. This table contains the following fields:

    - id: primary key
    - name: Human readable name for the interface referenced
    - interface_type: The type of interface represented
    - table_template: JSON specification for the interface table
    - ui_template: JSON specification for the interface UI
    - table_created: Has the table been created in the database?
    """

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    interface_type = Column(String(64), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    created_by_id = Column(
        Integer,
        ForeignKey("user.id", name="fk_node_created_by_id", use_alter=True),
        nullable=False,
    )
    created_by_user = relationship(
        "User", back_populates="interfaces_created", foreign_keys=[created_by_id]
    )
    updated_by_id = Column(
        Integer,
        ForeignKey("user.id", name="fk_node_updated_by_id", use_alter=True),
        nullable=False,
    )
    updated_by_user = relationship(
        "User", back_populates="interfaces_updated", foreign_keys=[updated_by_id]
    )

    __mapper_args__ = {
        "polymorphic_identity": "interface",
        "polymorphic_on": interface_type,
    }


class FormInputInterface(Interface):
    id = Column(Integer, ForeignKey("interface.id"), primary_key=True)
    template = Column(JSON, nullable=False)
    table_created = Column(Boolean, default=False)

    __mapper_args__ = {"polymorphic_identity": "form_input_interface"}


class QueryInterface(Interface):
    id = Column(Integer, ForeignKey("interface.id"), primary_key=True)
    template = Column(JSON, nullable=False)

    __mapper_args__ = {"polymorphic_identity": "query_interface"}
