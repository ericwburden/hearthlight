from datetime import date, timedelta
from random import randint
from sqlalchemy.orm import Session

from app import crud
from app.models.user import User
from app.tests.utils.utils import random_lower_string
from app.tests.utils.node import create_random_node


def test_create_form_input_table(db: Session, superuser: User) -> None:
    name = random_lower_string()
    date_created = date(1985, 1, 1) + timedelta(days=randint(0, 9999))
    an_integer = randint(0, 10000)
    node = create_random_node(db)
    form_input_table_create = {
        "name": name,
        "date_created": date_created,
        "an_integer": an_integer,
        "node_id": node.id,
    }
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    form_input_table_crud = crud.form_input.get_table_crud(db, id=form_input.id)
    form_input_table = form_input_table_crud.create(db, obj_in=form_input_table_create)
    assert form_input_table
    assert form_input_table.id
    assert form_input_table.name == name
    assert form_input_table.date_created == date_created
    assert form_input_table.an_integer == an_integer


def test_get_form_input_table(db: Session, superuser: User) -> None:
    name = random_lower_string()
    date_created = date(1985, 1, 1) + timedelta(days=randint(0, 9999))
    an_integer = randint(0, 10000)
    form_input_table_create = {
        "name": name,
        "date_created": date_created,
        "an_integer": an_integer,
    }
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    form_input_table_crud = crud.form_input.get_table_crud(db, id=form_input.id)
    form_input_table = form_input_table_crud.create(db, obj_in=form_input_table_create)
    stored_form_input = form_input_table_crud.get(db, id=form_input_table.id)
    assert stored_form_input
    assert stored_form_input.id == form_input_table.id
    assert stored_form_input.name == form_input_table.name
    assert stored_form_input.date_created == form_input_table.date_created
    assert stored_form_input.an_integer == form_input_table.an_integer


def test_get_multi_form_input_table(db: Session, superuser: User) -> None:
    names = [random_lower_string() for i in range(10)]
    dates = [date(1985, 1, 1) + timedelta(days=randint(0, 9999)) for i in range(10)]
    integers = [randint(0, 10000) for i in range(10)]
    form_input_creates = [
        {"name": names[i], "date_created": dates[i], "an_integer": integers[i]}
        for i in range(10)
    ]
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    form_input_table_crud = crud.form_input.get_table_crud(db, id=form_input.id)
    for form_input_create in form_input_creates:
        form_input_table_crud.create(db, obj_in=form_input_create)
    stored_form_inputs = form_input_table_crud.get_multi(db=db)
    for fic in form_input_creates:
        found_match = False
        for sfi in stored_form_inputs:
            name_match = fic["name"] == sfi.name
            date_match = fic["date_created"] == sfi.date_created
            integer_match = fic["an_integer"] == sfi.an_integer
            if name_match and date_match and integer_match:
                found_match = True
                break
        assert found_match


def test_update_form_input_table(db: Session, superuser: User) -> None:
    name = random_lower_string()
    date_created = date(1985, 1, 1) + timedelta(days=randint(0, 9999))
    an_integer = randint(0, 10000)
    form_input_create = {
        "name": name,
        "date_created": date_created,
        "an_integer": an_integer,
    }
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    form_input_crud = crud.form_input.get_table_crud(db, id=form_input.id)
    form_input_table = form_input_crud.create(db, obj_in=form_input_create)

    name2 = random_lower_string()
    form_input_update = {"name": name2}
    form_input_table2 = form_input_crud.update(
        db=db, db_obj=form_input_table, obj_in=form_input_update
    )
    assert form_input_table2
    assert form_input_table.id == form_input_table2.id
    assert form_input_table.name == form_input_table2.name
    assert form_input_table2.name == name2


def test_delete_form_input_table(db: Session, superuser: User) -> None:
    name = random_lower_string()
    date_created = date(1985, 1, 1) + timedelta(days=randint(0, 9999))
    an_integer = randint(0, 10000)
    form_input_create = {
        "name": name,
        "date_created": date_created,
        "an_integer": an_integer,
    }
    form_input = crud.form_input.get_by_template_table_name(
        db, table_name="form_input_test_table"
    )
    form_input_crud = crud.form_input.get_table_crud(db, id=form_input.id)
    form_input_table = form_input_crud.create(db, obj_in=form_input_create)
    form_input_table2 = form_input_crud.remove(db, id=form_input_table.id)
    form_input_table3 = form_input_crud.get(db=db, id=form_input_table.id)
    assert form_input_table3 is None
    assert form_input_table2.id == form_input_table.id
    assert form_input_table2.name == name
