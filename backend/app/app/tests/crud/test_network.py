from sqlalchemy.orm import Session

from app import crud
from app.models.user import User
from app.schemas.network import NetworkCreate, NetworkUpdate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def test_create_network(db: Session, normal_user: User) -> None:
    network_in = NetworkCreate(name=random_lower_string())
    network = crud.network.create(db=db, obj_in=network_in, created_by_id=normal_user.id)
    assert network.created_by_id == normal_user.id


def test_get_network(db: Session, normal_user: User) -> None:
    network_in = NetworkCreate(name=random_lower_string())
    network = crud.network.create(db=db, obj_in=network_in, created_by_id=normal_user.id)
    stored_network = crud.network.get(db=db, id=network.id)
    assert stored_network
    assert network.id == stored_network.id
    assert network.name == stored_network.name


def test_get_multi_network(db: Session, normal_user: User) -> None:
    names = [random_lower_string() for n in range(10)]
    new_networks_in = [NetworkCreate(name=name) for name in names]
    new_networks = [crud.network.create(db=db, obj_in=network_in, created_by_id=normal_user.id) for network_in in new_networks_in]
    stored_networks = crud.network.get_multi(db=db)
    stored_network_names = [sn.name for sn in stored_networks]
    for n in names:
        assert n in stored_network_names       


def test_update_network(db: Session, normal_user: User) -> None:
    name = random_lower_string()
    network_in = NetworkCreate(name=name)
    network = crud.network.create(db=db, obj_in=network_in, created_by_id=normal_user.id)
    name2 = random_lower_string()
    network_update = NetworkCreate(name=name2)
    network2 = crud.network.update(db=db, db_obj=network, obj_in=network_update, updated_by_id=normal_user.id)
    assert network.id == network2.id
    assert network.name == network2.name
    assert network.name == name2
    assert network.created_by_id == network2.created_by_id


def test_delete_network(db: Session, normal_user: User) -> None:
    name = random_lower_string()
    network_in = NetworkCreate(name=name)
    network = crud.network.create(db=db, obj_in=network_in, created_by_id=normal_user.id)
    network2 = crud.network.remove(db=db, id=network.id)
    network3 = crud.network.get(db=db, id=network.id)
    assert network3 is None
    assert network2.id == network.id
    assert network2.name == name
    assert network2.created_by_id == normal_user.id
