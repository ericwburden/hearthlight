from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app import crud
from app.models import Interface
from app.schemas import InterfaceCreate, TableTemplate, ColumnTemplate
from app.tests.utils.utils import random_lower_string


def test_table_template(name: Optional[str] = None) -> Dict[str, Any]:
    if not name:
        name = random_lower_string()
    return TableTemplate(
        table_name=name,
        columns=[
            ColumnTemplate(
                column_name="id",
                data_type="Integer",
                kwargs={"primary_key": True, "index": True},
            )
        ],
    )


def create_random_interface(db: Session, table_name: Optional[str] = None) -> Interface:
    interface_in = InterfaceCreate(
        name=random_lower_string(),
        interface_type="test",
        table_template=test_table_template(name=table_name),
    )
    interface = crud.interface.create(db, obj_in=interface_in, created_by_id=1)
    return interface
