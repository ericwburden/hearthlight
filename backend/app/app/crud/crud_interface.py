from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import *

from app.crud.base import CRUDBaseLogging
from app.db.base_class import Base, Default
from app.db.session import engine
from app.models.interface import Interface
from app.schemas.interface import InterfaceCreate, InterfaceUpdate, TableTemplate, ColumnTemplate


class CRUDInterface(CRUDBaseLogging[Interface, InterfaceCreate, InterfaceUpdate]):
    def get_by_template_table_name(self, db: Session, *, table_name: str) -> Interface:
        query = db.query(Interface).filter(
            Interface.table_template["table_name"].astext == table_name
        )
        return query.first()

    def create_template_table(self, db: Session, *, id: int) -> Interface:
        interface = db.query(Interface).get(id)
        table_template = TableTemplate(**interface.table_template)
        new_table = self.template_to_table_def(table_template, (Base, Default))
        new_table.__table__.create(engine)
        interface.table_created = True
        db.add(interface)
        db.commit()
        db.refresh(interface)
        return interface

    def template_to_table_def(
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
            c.column_name: self.unpack_column_def(c) 
            for c in template.columns
        }
        return type(table_name, base_class, columns)

    def unpack_column_def(self, template: ColumnTemplate) -> Column:
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


interface = CRUDInterface(Interface)
