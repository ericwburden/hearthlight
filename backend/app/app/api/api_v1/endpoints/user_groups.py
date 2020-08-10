from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()
user_group_create_validator = deps.UserPermissionValidator(
    schemas.ResourceTypeEnum.node, schemas.PermissionTypeEnum.create
)


@router.post("/", response_model=schemas.UserGroup)
def create_user_group(
    *,
    db: Session = Depends(deps.get_db),
    user_group_in: schemas.UserGroupCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> models.UserGroup:
    # Fail if the node for node_id doesn't exist
    node = crud.node.get(db, id=user_group_in.node_id)
    if not node:
        raise HTTPException(
            status_code=404, detail="Cannot find node indicated by node_id."
        )

    # Fail if normal user doesn't have create permission on parent node
    user_has_permission = user_group_create_validator.check_permission(
        user_group_in.node_id, db, current_user
    )
    if not user_has_permission and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="User does not have permission to create this node.",
        )

    user_group = crud.user_group.create(
        db, obj_in=user_group_in, created_by_id=current_user.id
    )
    return user_group
