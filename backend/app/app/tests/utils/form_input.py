from datetime import date, timedelta
from random import randint
from sqlalchemy.orm import Session

from app import crud
from app.tests.utils.node import create_random_node
from app.tests.utils.utils import random_lower_string


def create_random_form_input(db: Session):
    node = create_random_node(db)
    data = {
        "name": random_lower_string(),
        "date_created": str(date(1985, 1, 1) + timedelta(days=randint(0, 9999))),
        "an_integer": randint(0, 10000),
        "node_id": node.id,
    }
    interface = crud.interface.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    form_input_crud = crud.interface.get_interface_crud(db, id=interface.id)
    return form_input_crud.create(db, obj_in=data)
