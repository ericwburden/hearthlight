from pydantic import BaseModel, create_model
from pydantic.generics import GenericModel

# from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.engine import reflection
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar

from app.db.session import engine

# -----------------------------------------------------------------------------
# region | Functions to generate schema from JSON -----------------------------
# -----------------------------------------------------------------------------


def get_generic_schema(table_name: str) -> BaseModel:
    """From a given table name, generate a generic Pydantic model

    Args:
        table_name (str): The name of the database table to model

    Returns:
        BaseModel: A Pydantic model
    """
    inspector = reflection.Inspector.from_engine(engine)
    table_columns = inspector.get_columns(table_name)
    column_precursors = [_column_def_to_field(ct) for ct in table_columns]
    columns = {cp[0]: cp[1] for cp in column_precursors if cp}
    return create_model(table_name, **columns)


def _column_def_to_field(template: Dict[str, Any]) -> Optional[Tuple[Any]]:
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


# -----------------------------------------------------------------------------
# endregion -------------------------------------------------------------------
# -----------------------------------------------------------------------------
# region | Pre-defined generic schema -----------------------------------------
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# endregion -------------------------------------------------------------------
# -----------------------------------------------------------------------------
