from pydantic import BaseModel, create_model
from sqlalchemy.orm import Session
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Date,
)  # noqa: F401
from sqlalchemy.engine import reflection
from typing import Dict, Any, Tuple, Union, Optional

from app.crud.base import CRUDBaseLogging
from app.db.base_class import Base, Default
from app.db.session import engine
from app.crud.interfaces import CRUDInterfaceFormInput
from app.models.interface import Interface
from app.schemas.interface import (
    InterfaceCreate,
    InterfaceUpdate,
    TableTemplate,
    ColumnTemplate,
)


class CRUDInterface(CRUDBaseLogging[Interface, InterfaceCreate, InterfaceUpdate]):
    def get_by_template_table_name(self, db: Session, *, table_name: str) -> Interface:
        query = db.query(Interface).filter(
            Interface.table_template["table_name"].astext == table_name
        )
        return query.first()

    def get_interface_crud(self, db: Session, *, id: int) -> CRUDInterfaceFormInput:
        interface = db.query(Interface).get(id)
        return CRUDInterfaceFormInput(interface.table_template["table_name"])

    def create_template_table(self, db: Session, *, id: int) -> Interface:
        """Add a table to the database from an interface template

        Args:
            db (Session): SQLAlchemy Session
            id (int): Primary key ID for the interface

        Returns:
            Interface: The interface housing the table template
        """
        interface = db.query(Interface).get(id)
        table_template = TableTemplate(**interface.table_template)
        new_table = self._template_to_table_def(table_template, (Base, Default))
        new_table.__table__.create(engine)
        interface.table_created = True
        db.add(interface)
        db.commit()
        db.refresh(interface)
        return interface

    def _template_to_table_def(
        self, template: TableTemplate, base_class: Tuple[Any]
    ) -> Base:
        """Converts a table template to a table object

        Args:
            template (TableTemplate): Object specifying the table to
            create
            base_class (Tuple[Any]): Classes for the table to subclass
            from, one of which must be a SQLAlchemy declarative base

        Returns:
            Base: A table class, subclassed from SQLAlchemy declarative
            base
        """
        table_name = template.table_name
        columns = {
            c.column_name: self._column_def_to_column(c) for c in template.columns
        }
        return type(table_name, base_class, columns)

    def _column_def_to_column(self, template: ColumnTemplate) -> Column:
        """Given a column def dictionary, return a Column

        Args:
            template (Dict[str, str]): A dictionary from
            json_to_table_def()

        Returns:
            Column: The Column
        """
        data_type = template.data_type
        kwargs_str = ", ".join([f"{k}={v}" for k, v in template.kwargs.items()])
        column_str = f"Column({data_type}, {kwargs_str})"
        return eval(column_str)

    def get_validation_model(self, db: Session, *, table_name: str) -> BaseModel:
        """From a given table name, generate a generic Pydantic model

        Args:
            db (Session): SQLAlchemy Session
            table_name (str): The name of the database table to model

        Returns:
            BaseModel: A Pydantic model
        """
        inspector = reflection.Inspector.from_engine(engine)
        table_columns = inspector.get_columns(table_name)
        column_precursors = [self._column_def_to_field(ct) for ct in table_columns]
        columns = {cp[0]: cp[1] for cp in column_precursors if cp}
        return create_model(table_name, **columns)

    def _column_def_to_field(self, template: Dict[str, Any]) -> Optional[Tuple[Any]]:
        """Transform SQLAlchemy column mapping to Pydantic field
        definition

        Args:
            template (Dict[str, Any]): A SQLAlchemy column mapping from
            Inspector.get_columns('table_name')

        Returns:
            Optional[Tuple[Any]]: A tuple of (field_name, field_definition)
        """
        if template.get("autoincrement"):
            return None
        data_type = template.get("type").python_type
        data_def = (data_type, ...)
        if template.get("nullable"):
            data_def = (data_type, None)
        if template.get("default") and not template.get("autoincrement"):
            data_def = (data_type, template.get("default"))
        return (template.get("name"), data_def)


interface = CRUDInterface(Interface)
