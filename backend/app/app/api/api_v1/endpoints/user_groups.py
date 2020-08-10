from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.UserGroup)
def create_user_group(
    *, 
    db: Session = Depends(deps.get_db), 
    user_group_in: schemas.UserGroupCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> models.UserGroup:
    user_group = crud.user_group.create(db, obj_in=user_group_in, created_by_id=current_user.id)
    return user_group
