from sqlalchemy.orm import Session

from app import crud
from app.models.user import User
from app.schemas.user_group import UserGroupCreate, UserGroupUpdate
from app.tests.utils.user import create_random_user
from app.tests.utils.node import create_random_node
from app.tests.utils.utils import random_lower_string


def test_create_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(db, created_by_id=normal_user.id, node_type='test_create_user_group')
    user_group_in = UserGroupCreate(name=random_lower_string(), node_id=node.id)
    user_group = crud.user_group.create(db=db, obj_in=user_group_in, created_by_id=normal_user.id)
    assert user_group.created_by_id == normal_user.id


def test_get_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(db, created_by_id=normal_user.id, node_type='test_get_user_group')
    user_group_in = UserGroupCreate(name=random_lower_string(), node_id=node.id)
    user_group = crud.user_group.create(db=db, obj_in=user_group_in, created_by_id=normal_user.id)
    stored_user_group = crud.user_group.get(db=db, id=user_group.id)
    assert stored_user_group
    assert user_group.id == stored_user_group.id
    assert user_group.name == stored_user_group.name
    assert node.id == stored_user_group.node_id


def test_get_multi_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(db, created_by_id=normal_user.id, node_type='test_get_multi_user_group')
    names = [random_lower_string() for n in range(10)]
    new_user_groups_in = [UserGroupCreate(name=name, node_id=node.id) for name in names]
    new_user_groups = [
        crud.user_group.create(db=db, obj_in=user_group_in, created_by_id=normal_user.id)
        for user_group_in in new_user_groups_in
    ]
    stored_user_groups = crud.user_group.get_multi(db=db)
    stored_user_group_names = [sn.name for sn in stored_user_groups]
    for n in names:
        assert n in stored_user_group_names


def test_update_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(db, created_by_id=normal_user.id, node_type='test_update_user_group')
    name = random_lower_string()
    user_group_in = UserGroupCreate(name=name, node_id=node.id)
    user_group = crud.user_group.create(db=db, obj_in=user_group_in, created_by_id=normal_user.id)
    name2 = random_lower_string()
    user_group_update = UserGroupUpdate(name=name2)
    user_group2 = crud.user_group.update(
        db=db, db_obj=user_group, obj_in=user_group_update, updated_by_id=normal_user.id
    )
    assert user_group.id == user_group2.id
    assert user_group.name == user_group2.name
    assert user_group.name == name2
    assert user_group.created_by_id == user_group2.created_by_id


def test_delete_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(db, created_by_id=normal_user.id, node_type='test_delete_user_group')
    name = random_lower_string()
    user_group_in = UserGroupCreate(name=name, node_id=node.id)
    user_group = crud.user_group.create(db=db, obj_in=user_group_in, created_by_id=normal_user.id)
    user_group2 = crud.user_group.remove(db=db, id=user_group.id)
    user_group3 = crud.user_group.get(db=db, id=user_group.id)
    assert user_group3 is None
    assert user_group2.id == user_group.id
    assert user_group2.name == name
    assert user_group2.created_by_id == normal_user.id


def test_add_user_to_user_group(db: Session, normal_user: User) -> None:
    node = create_random_node(db, created_by_id=normal_user.id, node_type='test_add_user_to_user_group')
    name = random_lower_string()
    user_group_in = UserGroupCreate(name=name, node_id=node.id)
    user_group = crud.user_group.create(db=db, obj_in=user_group_in, created_by_id=normal_user.id)
    user = create_random_user(db)
    
    association = crud.user_group.add_user_to_group(db=db, user_group=user_group, user=user)
    assert association.user_group_id == user_group.id
    assert association.user_id == user.id