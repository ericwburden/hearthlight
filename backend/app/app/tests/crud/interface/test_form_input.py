import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import InvalidRequestError

from app import crud
from app.models.user import User
from app.schemas.interface import FormInputCreate, FormInputUpdate
from app.tests.utils.interface import test_table_template
from app.tests.utils.utils import random_lower_string


FORM_INPUT_INTERFACE_TYPE = "form_input_interface"

# --------------------------------------------------------------------------------------
# region Tests for basic CRUD fuctions by superuser ------------------------------------
# --------------------------------------------------------------------------------------


def test_create_form_input(db: Session, superuser: User) -> None:
    name = random_lower_string()
    table_template = test_table_template()
    form_input_in = FormInputCreate(name=name, template=table_template)
    form_input = crud.form_input.create(
        db=db, obj_in=form_input_in, created_by_id=superuser.id
    )
    assert form_input
    assert form_input.name == name
    assert form_input.template == table_template
    assert form_input.interface_type == FORM_INPUT_INTERFACE_TYPE
    assert form_input.table_created is False
    assert form_input.created_by_id == superuser.id


def test_get_form_input(db: Session, superuser: User) -> None:
    name = random_lower_string()
    table_template = test_table_template()
    form_input_in = FormInputCreate(name=name, template=table_template)
    form_input = crud.form_input.create(
        db=db, obj_in=form_input_in, created_by_id=superuser.id
    )
    stored_form_input = crud.form_input.get(db=db, id=form_input.id)
    assert stored_form_input
    assert form_input.name == stored_form_input.name
    assert form_input.template == stored_form_input.template
    assert form_input.interface_type == FORM_INPUT_INTERFACE_TYPE
    assert form_input.table_created is False
    assert form_input.created_by_id == stored_form_input.created_by_id


def test_get_multi_form_input(db: Session, superuser: User) -> None:
    names = [random_lower_string() for i in range(10)]
    table_template = test_table_template()
    new_form_inputs_in = [
        FormInputCreate(name=n, template=table_template) for n in names
    ]
    [
        crud.form_input.create(db=db, obj_in=form_input_in, created_by_id=superuser.id)
        for form_input_in in new_form_inputs_in
    ]
    stored_form_inputs = crud.form_input.get_multi(db=db)
    for nii in new_form_inputs_in:
        found_match = False
        for si in stored_form_inputs:
            name_match = nii.name == si.name
            table_template_match = nii.template == si.template
            if name_match and table_template_match:
                found_match = True
                break
        assert found_match


def test_update_form_input(db: Session, superuser: User) -> None:
    name = random_lower_string()
    table_template = test_table_template()
    form_input_in = FormInputCreate(name=name, template=table_template)
    form_input = crud.form_input.create(
        db=db, obj_in=form_input_in, created_by_id=superuser.id
    )
    name2 = random_lower_string()
    form_input_update = FormInputUpdate(name=name2)
    form_input2 = crud.form_input.update(
        db=db, db_obj=form_input, obj_in=form_input_update, updated_by_id=superuser.id
    )
    assert form_input.id == form_input2.id
    assert form_input.name == form_input2.name
    assert form_input2.name == name2
    assert form_input.updated_by_id == superuser.id


def test_delete_form_input(db: Session, superuser: User) -> None:
    name = random_lower_string()
    table_template = test_table_template()
    form_input_in = FormInputCreate(name=name, template=table_template)
    form_input = crud.form_input.create(
        db=db, obj_in=form_input_in, created_by_id=superuser.id
    )
    form_input2 = crud.form_input.remove(db, id=form_input.id)
    form_input3 = crud.form_input.get(db=db, id=form_input.id)
    assert form_input3 is None
    assert form_input2.id == form_input.id
    assert form_input2.name == name
    assert form_input2.created_by_id == superuser.id


def test_create_table_from_template(db: Session, superuser: User) -> None:
    name = random_lower_string()
    table_template = test_table_template()
    form_input_in = FormInputCreate(name=name, template=table_template)
    form_input = crud.form_input.create(
        db=db, obj_in=form_input_in, created_by_id=superuser.id
    )
    form_input_post_create = crud.form_input.create_template_table(
        db=db, id=form_input.id
    )
    assert form_input_post_create
    assert form_input_post_create.table_created


@pytest.mark.filterwarnings("ignore")
def test_create_table_from_template_fail_exists(db: Session, superuser: User) -> None:
    name = random_lower_string()
    table_template = test_table_template()
    form_input_in = FormInputCreate(name=name, template=table_template)
    form_input = crud.form_input.create(
        db=db, obj_in=form_input_in, created_by_id=superuser.id
    )
    crud.form_input.create_template_table(db=db, id=form_input.id)
    with pytest.raises(InvalidRequestError) as e:
        crud.form_input.create_template_table(db=db, id=form_input.id)
    assert str(e.value) == (
        f"Table '{table_template.table_name}' is already defined for this MetaData"
        f" instance.  Specify 'extend_existing=True' to redefine options and columns "
        f"on an existing Table object."
    )
