from sqlalchemy.orm import Session

from app import crud
from app.models.user import User
from app.schemas.node import NodeCreate, NodeUpdate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def test_create_node(db: Session, normal_user: User) -> None:
    node_in = NodeCreate(name=random_lower_string(), node_type="node")
    node = crud.node.create(db=db, obj_in=node_in, created_by_id=normal_user.id)
    assert node.created_by_id == normal_user.id


def test_get_node(db: Session, normal_user: User) -> None:
    node_in = NodeCreate(name=random_lower_string(), node_type="node")
    node = crud.node.create(db=db, obj_in=node_in, created_by_id=normal_user.id)
    stored_node = crud.node.get(db=db, id=node.id)
    assert stored_node
    assert node.id == stored_node.id
    assert node.name == stored_node.name


def test_get_multi_node(db: Session, normal_user: User) -> None:
    names = [random_lower_string() for n in range(10)]
    new_nodes_in = [NodeCreate(name=name, node_type="node") for name in names]
    new_nodes = [
        crud.node.create(db=db, obj_in=node_in, created_by_id=normal_user.id)
        for node_in in new_nodes_in
    ]
    stored_nodes = crud.node.get_multi(db=db)
    stored_node_names = [sn.name for sn in stored_nodes]
    for n in names:
        assert n in stored_node_names


def test_update_node(db: Session, normal_user: User) -> None:
    name = random_lower_string()
    node_in = NodeCreate(name=name, node_type="node")
    node = crud.node.create(db=db, obj_in=node_in, created_by_id=normal_user.id)
    name2 = random_lower_string()
    node_update = NodeUpdate(name=name2)
    node2 = crud.node.update(
        db=db, db_obj=node, obj_in=node_update, updated_by_id=normal_user.id
    )
    assert node.id == node2.id
    assert node.name == node2.name
    assert node.name == name2
    assert node.created_by_id == node2.created_by_id


def test_delete_node(db: Session, normal_user: User) -> None:
    name = random_lower_string()
    node_in = NodeCreate(name=name, node_type="node")
    node = crud.node.create(db=db, obj_in=node_in, created_by_id=normal_user.id)
    node2 = crud.node.remove(db=db, id=node.id)
    node3 = crud.node.get(db=db, id=node.id)
    assert node3 is None
    assert node2.id == node.id
    assert node2.name == name
    assert node2.created_by_id == normal_user.id


def test_create_child_node(db: Session, normal_user: User) -> None:
    parent_node_in = NodeCreate(name=random_lower_string(), node_type="network")
    parent_node = crud.node.create(
        db=db, obj_in=parent_node_in, created_by_id=normal_user.id
    )

    child_node_in = NodeCreate(
        name=random_lower_string(), node_type="node", parent_id=parent_node.id
    )
    child_node = crud.node.create(
        db=db, obj_in=child_node_in, created_by_id=normal_user.id
    )

    assert child_node.parent_id == parent_node.id
    assert child_node.depth == parent_node.depth + 1
    assert parent_node.created_by_id == normal_user.id
    assert child_node.created_by_id == normal_user.id


def test_get_node_descendants(db: Session, normal_user: User) -> None:
    parent_node_in = NodeCreate(name=random_lower_string(), node_type="network")
    parent_node = crud.node.create(
        db=db, obj_in=parent_node_in, created_by_id=normal_user.id
    )

    # Child of parent_node
    child_node1_in = NodeCreate(
        name=random_lower_string(), node_type="node", parent_id=parent_node.id
    )
    child_node1 = crud.node.create(
        db=db, obj_in=child_node1_in, created_by_id=normal_user.id
    )

    # Child of parent_node
    child_node2_in = NodeCreate(
        name=random_lower_string(), node_type="node", parent_id=parent_node.id
    )
    child_node2 = crud.node.create(
        db=db, obj_in=child_node2_in, created_by_id=normal_user.id
    )

    # Child of child_node2
    child_node3_in = NodeCreate(
        name=random_lower_string(), node_type="node", parent_id=child_node2.id
    )
    child_node3 = crud.node.create(
        db=db, obj_in=child_node3_in, created_by_id=normal_user.id
    )

    # Node not related to others
    outlaw_node_in = NodeCreate(name=random_lower_string(), node_type="node")
    outlaw_node = crud.node.create(
        db=db, obj_in=outlaw_node_in, created_by_id=normal_user.id
    )

    nodes = crud.node.get_children(db, id=parent_node.id)
    node_ids = [n.id for n in nodes]

    assert len(nodes) == 4
    assert outlaw_node.id not in node_ids
    for node in nodes:
        assert node.id in [
            parent_node.id,
            child_node1.id,
            child_node2.id,
            child_node3.id,
        ]
        assert node.parent_id in [parent_node.id, child_node2.id] or not node.parent_id
        assert node.parent_id not in [child_node1.id, child_node3.id, outlaw_node.id]
