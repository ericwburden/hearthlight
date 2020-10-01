import random
from sqlalchemy.orm import Session

from app import crud
from app.models.user import User
from app.schemas.node import NodeCreate, NodeUpdate
from app.schemas.permission import PermissionTypeEnum
from app.schemas.user_group import UserGroupCreate
from app.tests.utils.form_input import create_random_form_input_interface
from app.tests.utils.user import create_random_user
from app.tests.utils.user_group import create_random_user_group
from app.tests.utils.node import create_random_node
from app.tests.utils.utils import random_lower_string


# --------------------------------------------------------------------------------------
# region Tests for basic CRUD fuctions by superuser ------------------------------------
# --------------------------------------------------------------------------------------
def test_create_node(db: Session, superuser: User) -> None:
    node_in = NodeCreate(name=random_lower_string(), node_type="node")
    node = crud.node.create(db=db, obj_in=node_in, created_by_id=superuser.id)
    assert node.created_by_id == superuser.id


def test_get_node(db: Session, superuser: User) -> None:
    node_in = NodeCreate(name=random_lower_string(), node_type="node")
    node = crud.node.create(db=db, obj_in=node_in, created_by_id=superuser.id)
    stored_node = crud.node.get(db=db, id=node.id)
    assert stored_node
    assert node.id == stored_node.id
    assert node.name == stored_node.name


def test_get_multi_node(db: Session, superuser: User) -> None:
    names = [random_lower_string() for n in range(10)]
    new_nodes_in = [NodeCreate(name=name, node_type="node") for name in names]
    [
        crud.node.create(db=db, obj_in=node_in, created_by_id=superuser.id)
        for node_in in new_nodes_in
    ]
    stored_nodes = crud.node.get_multi(db=db)
    stored_node_names = [sn.name for sn in stored_nodes]
    for n in names:
        assert n in stored_node_names


def test_get_multi_network(db: Session, superuser: User) -> None:
    names = [random_lower_string() for n in range(10)]
    new_networks_in = [NodeCreate(name=name, node_type="network") for name in names]
    [
        crud.node.create(db=db, obj_in=node_in, created_by_id=superuser.id)
        for node_in in new_networks_in
    ]
    new_node_in = NodeCreate(name=random_lower_string(), node_type="something_else")
    new_node = crud.node.create(db=db, obj_in=new_node_in, created_by_id=superuser.id)
    stored_nodes = crud.node.get_multi_networks(db=db)
    stored_node_names = [sn.name for sn in stored_nodes]
    for n in names:
        assert n in stored_node_names
    assert new_node.name not in stored_node_names


def test_update_node(db: Session, superuser: User) -> None:
    name = random_lower_string()
    node_in = NodeCreate(name=name, node_type="node")
    node = crud.node.create(db=db, obj_in=node_in, created_by_id=superuser.id)
    name2 = random_lower_string()
    node_update = NodeUpdate(name=name2)
    node2 = crud.node.update(
        db=db, db_obj=node, obj_in=node_update, updated_by_id=superuser.id
    )
    assert node.id == node2.id
    assert node.name == node2.name
    assert node.name == name2
    assert node.created_by_id == node2.created_by_id


def test_delete_node(db: Session, superuser: User) -> None:
    name = random_lower_string()
    node_in = NodeCreate(name=name, node_type="node")
    node = crud.node.create(db=db, obj_in=node_in, created_by_id=superuser.id)
    node2 = crud.node.remove(db=db, id=node.id)
    node3 = crud.node.get(db=db, id=node.id)
    assert node3 is None
    assert node2.id == node.id
    assert node2.name == name
    assert node2.created_by_id == superuser.id


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for tree structure CRUD operations --------------------------------------
# --------------------------------------------------------------------------------------


def test_create_child_node(db: Session, superuser: User) -> None:
    parent_node_in = NodeCreate(name=random_lower_string(), node_type="network")
    parent_node = crud.node.create(
        db=db, obj_in=parent_node_in, created_by_id=superuser.id
    )

    child_node_in = NodeCreate(
        name=random_lower_string(), node_type="node", parent_id=parent_node.id
    )
    child_node = crud.node.create(
        db=db, obj_in=child_node_in, created_by_id=superuser.id
    )

    assert child_node.parent_id == parent_node.id
    assert child_node.depth == parent_node.depth + 1
    assert parent_node.created_by_id == superuser.id
    assert child_node.created_by_id == superuser.id


def test_get_node_descendants(db: Session, superuser: User) -> None:
    parent_node_in = NodeCreate(name=random_lower_string(), node_type="network")
    parent_node = crud.node.create(
        db=db, obj_in=parent_node_in, created_by_id=superuser.id
    )

    # Child of parent_node
    child_node1_in = NodeCreate(
        name=random_lower_string(), node_type="node", parent_id=parent_node.id
    )
    child_node1 = crud.node.create(
        db=db, obj_in=child_node1_in, created_by_id=superuser.id
    )

    # Child of parent_node
    child_node2_in = NodeCreate(
        name=random_lower_string(), node_type="node", parent_id=parent_node.id
    )
    child_node2 = crud.node.create(
        db=db, obj_in=child_node2_in, created_by_id=superuser.id
    )

    # Child of child_node2
    child_node3_in = NodeCreate(
        name=random_lower_string(), node_type="node", parent_id=child_node2.id
    )
    child_node3 = crud.node.create(
        db=db, obj_in=child_node3_in, created_by_id=superuser.id
    )

    # Node not related to others
    outlaw_node_in = NodeCreate(name=random_lower_string(), node_type="node")
    outlaw_node = crud.node.create(
        db=db, obj_in=outlaw_node_in, created_by_id=superuser.id
    )

    nodes = crud.node.get_child_nodes(db, id=parent_node.id)
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


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for permission CRUD operations ------------------------------------------
# --------------------------------------------------------------------------------------


def test_node_get_permissions(db: Session, superuser: User) -> None:
    node_in = NodeCreate(name=random_lower_string(), node_type="node")
    node = crud.node.create(db=db, obj_in=node_in, created_by_id=superuser.id)
    stored_permissions = crud.node.get_permissions(db, id=node.id)
    for pt in list(PermissionTypeEnum):
        assert pt in [p.permission_type for p in stored_permissions]


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region Tests for CRUD with normal user and permissions -------------------------------
# --------------------------------------------------------------------------------------


def test_get_multi_node_with_permission(db: Session, superuser: User) -> None:
    # Create parent node
    parent_node_in = NodeCreate(
        name=random_lower_string(),
        node_type="test_get_multi_node_with_permission_parent",
    )
    parent_node = crud.node.create(
        db=db, obj_in=parent_node_in, created_by_id=superuser.id
    )

    # Create User Group attached to parent node
    user_group_in = UserGroupCreate(name=random_lower_string(), node_id=parent_node.id)
    user_group = crud.user_group.create(
        db, obj_in=user_group_in, created_by_id=superuser.id
    )

    # Create a normal user and add that user to the user group
    normal_user = create_random_user(db)
    crud.user_group.add_user(db, user_group=user_group, user_id=normal_user.id)

    # Create a bunch of child nodes (it doesn't matter whether or not they're attached
    # to the parent node)
    names = [random_lower_string() for n in range(10)]
    new_nodes_in = [
        NodeCreate(
            name=name,
            node_type="test_get_multi_node_with_permission_other",
            parent_id=random.choice([parent_node.id, None]),
        )
        for name in names
    ]
    new_nodes = [
        crud.node.create(db=db, obj_in=node_in, created_by_id=superuser.id)
        for node_in in new_nodes_in
    ]

    # For each node, instantiate permissions, get the read permission, then add it to
    # the user group, enabled
    for node in new_nodes:
        node_read_permission = crud.node.get_permission(
            db, id=node.id, permission_type=PermissionTypeEnum.read
        )
        crud.permission.grant(
            db, user_group_id=user_group.id, permission_id=node_read_permission.id
        )

    # Create a new node, instantiate permissions, add it to the user group, disabled
    blocked_node = create_random_node(
        db, created_by_id=superuser.id, node_type="blocked", parent_id=parent_node.id
    )
    blocked_node_read_permission = crud.node.get_permission(
        db, id=blocked_node.id, permission_type=PermissionTypeEnum.read
    )
    crud.permission.grant(
        db, user_group_id=user_group.id, permission_id=blocked_node_read_permission.id
    )
    crud.permission.revoke(
        db, user_group_id=user_group.id, permission_id=blocked_node_read_permission.id
    )

    # Get the nodes back with permission requirements and ensure that you get back
    # all the nodes we just put in with permissions and that you don't get the
    # blocked node
    stored_nodes = crud.node.get_multi_with_permissions(db=db, user=normal_user)
    stored_node_names = [sn.name for sn in stored_nodes]
    for n in names:
        assert n in stored_node_names
    assert blocked_node.name not in stored_node_names


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests to modify interfaces attached to a node -------------------------------
# --------------------------------------------------------------------------------------


def test_add_interface_to_node(db: Session, superuser: User) -> None:
    node = create_random_node(db)
    interface = create_random_form_input_interface(db)
    result = crud.node.add_interface(db, node=node, interface=interface)
    assert result is node
    assert interface in node.interfaces


def test_remove_interface_from_node(db: Session, superuser: User) -> None:
    node = create_random_node(db)
    interface = create_random_form_input_interface(db)
    crud.node.add_interface(db, node=node, interface=interface)
    result = crud.node.remove_interface(db, node=node, interface=interface)
    assert result is node
    assert interface not in node.interfaces


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# region | Tests to fetch node children ------------------------------------------------
# --------------------------------------------------------------------------------------


def test_get_node_children(db: Session, superuser: User) -> None:
    node = create_random_node(db)
    user_group = create_random_user_group(db, node_id=node.id)
    child_node = create_random_node(db, parent_id=node.id)
    interface = create_random_form_input_interface(db)
    crud.node.add_interface(db, node=node, interface=interface)
    result = crud.node.get_node_children(db, id=node.id)

    for node_child in result:
        assert node_child.node_id == node.id
        if node_child.child_type == "interface":
            assert node_child.child_id == interface.id
        if node_child.child_type == "node":
            assert node_child.child_id == child_node.id
        if node_child.child_type == "user_group":
            assert node_child.child_id == user_group.id


# --------------------------------------------------------------------------------------
# endregion ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
