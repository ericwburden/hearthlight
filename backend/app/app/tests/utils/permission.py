import random
from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models
from app.schemas.permission import (
    PermissionCreate,
    PermissionTypeEnum,
    ResourceTypeEnum,
)
from app.tests.utils.node import create_random_node
from app.tests.utils.utils import random_lower_string


def create_random_permission(
    db: Session, *, node_id: Optional[int] = None
) -> models.Node:
    if node_id is None:
        node = create_random_node(
            db, created_by_id=created_by_id, node_type="random_node"
        )
        node_id = node.id
    permission_type = random.choice(list(PermissionTypeEnum))
    permission_in = PermissionCreate(
        resource_id=node_id,
        resource_type=ResourceTypeEnum.node,
        permission_type=permission_type,
    )
    return crud.node_permission.create(db=db, obj_in=permission_in)
