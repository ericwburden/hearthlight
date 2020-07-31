from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models
from app.schemas.node import NodeCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_node(
    db: Session,
    *,
    created_by_id: Optional[int] = None,
    node_type: Optional[str] = None,
    parent_id: Optional[int] = None,
    is_active: Optional[bool] = True,
) -> models.Node:
    if created_by_id is None:
        user = create_random_user(db)
        created_by_id = user.id
    if node_type is None:
        node_type = "node"
    name = random_lower_string()
    node_in = NodeCreate(
        name=name, node_type=node_type, parent_id=parent_id, is_active=is_active
    )
    return crud.node.create(db=db, obj_in=node_in, created_by_id=created_by_id)
