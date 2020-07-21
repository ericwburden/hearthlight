from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models
from app.schemas.user_group import UserGroupCreate
from app.tests.utils.node import create_random_node
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_user_group(
    db: Session, *, created_by_id: Optional[int] = None, node_id: Optional[int] = None
) -> models.Node:
    if created_by_id is None:
        user = create_random_user(db)
        created_by_id = user.id
    if node_id is None:
        node = create_random_node(
            db, created_by_id=created_by_id, node_type="random_node"
        )
        node_id = node.id
    user_group_in = UserGroupCreate(name=random_lower_string(), node_id=node.id)
    return crud.user_group.create(
        db=db, obj_in=user_group_in, created_by_id=created_by_id
    )
