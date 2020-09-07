import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import InvalidRequestError, SAWarning

from app import crud
from app.models.user import User
from app.schemas.interface import InterfaceCreate, InterfaceUpdate
from app.tests.utils.interface import test_table_template
from app.tests.utils.utils import random_lower_string

# --------------------------------------------------------------------------------------
# region Tests for basic CRUD fuctions by superuser ------------------------------------
# --------------------------------------------------------------------------------------


def test_create_interface(db: Session, superuser: User) -> None:
    name = random_lower_string()
    interface_type = "test"
    table_template = test_table_template()
    interface_in = InterfaceCreate(
        name=name, interface_type=interface_type, table_template=table_template
    )
    interface = crud.interface.create(
        db=db, obj_in=interface_in, created_by_id=superuser.id
    )
    assert interface
    assert interface.name == name
    assert interface.interface_type == interface_type
    assert interface.table_template == table_template
    assert interface.created_by_id == superuser.id


def test_get_interface(db: Session, superuser: User) -> None:
    name = random_lower_string()
    interface_type = "test"
    table_template = test_table_template()
    interface_in = InterfaceCreate(
        name=name, interface_type=interface_type, table_template=table_template
    )
    interface = crud.interface.create(
        db=db, obj_in=interface_in, created_by_id=superuser.id
    )
    stored_interface = crud.interface.get(db=db, id=interface.id)
    assert stored_interface
    assert interface.name == stored_interface.name
    assert interface.interface_type == stored_interface.interface_type
    assert interface.table_template == stored_interface.table_template
    assert interface.created_by_id == stored_interface.created_by_id


def test_get_multi_interface(db: Session, superuser: User) -> None:
    names = [random_lower_string() for i in range(10)]
    interface_type = "test"
    table_template = test_table_template()
    new_interfaces_in = [
        InterfaceCreate(
            name=n, interface_type=interface_type, table_template=table_template
        )
        for n in names
    ]
    [
        crud.interface.create(db=db, obj_in=interface_in, created_by_id=superuser.id)
        for interface_in in new_interfaces_in
    ]
    stored_interfaces = crud.interface.get_multi(db=db)
    for nii in new_interfaces_in:
        found_match = False
        for si in stored_interfaces:
            name_match = nii.name == si.name
            interface_type_match = nii.interface_type == si.interface_type
            table_template_match = nii.table_template == si.table_template
            if name_match and interface_type_match and table_template_match:
                found_match = True
                break
        assert found_match


def test_update_interface(db: Session, superuser: User) -> None:
    name = random_lower_string()
    interface_type = "test"
    table_template = test_table_template()
    interface_in = InterfaceCreate(
        name=name, interface_type=interface_type, table_template=table_template
    )
    interface = crud.interface.create(
        db=db, obj_in=interface_in, created_by_id=superuser.id
    )
    name2 = random_lower_string()
    interface_update = InterfaceUpdate(name=name2)
    interface2 = crud.interface.update(
        db=db, db_obj=interface, obj_in=interface_update, updated_by_id=superuser.id
    )
    assert interface.id == interface2.id
    assert interface.name == interface2.name
    assert interface2.name == name2
    assert interface.updated_by_id == superuser.id


def test_delete_interface(db: Session, superuser: User) -> None:
    name = random_lower_string()
    interface_type = "test"
    table_template = test_table_template()
    interface_in = InterfaceCreate(
        name=name, interface_type=interface_type, table_template=table_template
    )
    interface = crud.interface.create(
        db=db, obj_in=interface_in, created_by_id=superuser.id
    )
    interface2 = crud.interface.remove(db, id=interface.id)
    interface3 = crud.interface.get(db=db, id=interface.id)
    assert interface3 is None
    assert interface2.id == interface.id
    assert interface2.name == name
    assert interface2.created_by_id == superuser.id


def test_create_table_from_template(db: Session, superuser: User) -> None:
    name = random_lower_string()
    interface_type = "test"
    table_template = test_table_template()
    interface_in = InterfaceCreate(
        name=name, interface_type=interface_type, table_template=table_template
    )
    interface = crud.interface.create(
        db=db, obj_in=interface_in, created_by_id=superuser.id
    )
    interface_post_create = crud.interface.create_template_table(db=db, id=interface.id)
    assert interface_post_create
    assert interface_post_create.table_created


@pytest.mark.filterwarnings("ignore")
def test_create_table_from_template_fail_exists(db: Session, superuser: User) -> None:
    name = random_lower_string()
    interface_type = "test"
    table_template = test_table_template()
    interface_in = InterfaceCreate(
        name=name, interface_type=interface_type, table_template=table_template
    )
    interface = crud.interface.create(
        db=db, obj_in=interface_in, created_by_id=superuser.id
    )
    crud.interface.create_template_table(db=db, id=interface.id)
    with pytest.raises(InvalidRequestError) as e:
        crud.interface.create_template_table(db=db, id=interface.id)
    assert str(e.value) == (
        f"Table '{table_template['table_name']}' is already defined for this MetaData"
        f" instance.  Specify 'extend_existing=True' to redefine options and columns "
        f"on an existing Table object."
    )
    
