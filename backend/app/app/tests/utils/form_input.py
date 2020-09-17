from datetime import date, timedelta
from random import randint
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app import crud
from app.models import FormInputInterface
from app.schemas import (
    FormInputCreate,
    TableTemplate,
    ColumnTemplate,
)
from app.tests.utils.node import create_random_node
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


def create_random_form_input_interface(
    db: Session, table_name: Optional[str] = None
) -> FormInputInterface:
    form_input_in = FormInputCreate(
        name=random_lower_string(), template=test_table_template(name=table_name),
    )
    form_input = crud.form_input.create(db, obj_in=form_input_in, created_by_id=1)
    return form_input


def create_random_form_input_table_entry(db: Session):
    node = create_random_node(db)
    data = {
        "name": random_lower_string(),
        "date_created": str(date(1985, 1, 1) + timedelta(days=randint(0, 9999))),
        "an_integer": randint(0, 10000),
        "node_id": node.id,
    }
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    form_input_crud = crud.form_input.get_table_crud(db, id=form_input.id)
    return form_input_crud.create(db, obj_in=data)
