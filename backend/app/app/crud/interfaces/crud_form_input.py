from sqlalchemy import (  # noqa: F401
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Date,
)
from sqlalchemy.orm import Session
from typing import Any, Tuple

from app.db.base_class import Base, Default
from app.db.session import engine
from app.crud.base import AccessControl, CRUDBaseLogging, CRUDInterfaceBase
from app.models.interface import FormInputInterface
from app.models.permission import InterfacePermission
from app.schemas.interface import (
    FormInputCreate,
    FormInputUpdate,
    TableTemplate,
    ColumnTemplate,
)


class CRUDFormInputInterfaceTable(CRUDInterfaceBase):
    pass


class CRUDFormInputInterface(
    AccessControl[FormInputInterface, InterfacePermission],
    CRUDBaseLogging[FormInputInterface, FormInputCreate, FormInputUpdate],
):
    def get_by_template_table_name(
        self, db: Session, *, table_name: str
    ) -> FormInputInterface:
        query = db.query(FormInputInterface).filter(
            FormInputInterface.template["table_name"].astext == table_name
        )
        return query.first()

    def get_table_crud(self, db: Session, *, id: int) -> CRUDFormInputInterfaceTable:
        form_input = db.query(FormInputInterface).get(id)
        return CRUDFormInputInterfaceTable(id, form_input.template["table_name"])

    def create_template_table(self, db: Session, *, id: int) -> FormInputInterface:
        """Add a table to the database from an interface template

        Args:
            db (Session): SQLAlchemy Session
            id (int): Primary key ID for the interface

        Returns:
            FormInputInterface: The interface housing the table template
        """
        form_input = db.query(FormInputInterface).get(id)
        table_template = TableTemplate(**form_input.template)
        new_table = self._template_to_table_def(table_template, (Base, Default))
        new_table.__table__.create(engine)
        form_input.table_created = True
        db.add(form_input)
        db.commit()
        db.refresh(form_input)
        return form_input

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

        # Inject a foreign key to the interface table into the
        # table structure
        columns["interface_id"] = Column(
            Integer, ForeignKey("interface.id"), index=True, nullable=False
        )
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

        args = template.args if template.args else []
        args_str = ", ".join(args)
        kwargs = template.kwargs if template.kwargs else {}
        kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])

        parts = ", ".join(
            filter(lambda x: len(x) > 0, (data_type, args_str, kwargs_str))
        )
        column_str = f"Column({parts})"
        return eval(column_str)


form_input = CRUDFormInputInterface(FormInputInterface, InterfacePermission)
