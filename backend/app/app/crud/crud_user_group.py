from typing import List, Union, Dict, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql.expression import literal, literal_column

from app.crud.base import CRUDBaseLogging
from app.models.user import User
from app.models.user_group import UserGroup, UserGroupUser
from app.schemas.user_group import UserGroupCreate, UserGroupUpdate


class CRUDUserGroup(CRUDBaseLogging[UserGroup, UserGroupCreate, UserGroupUpdate]):
    def add_user_to_group(self, db: Session, *, user_group: UserGroup, user: User):
        user_group.users.append(user)
        db.commit()
        q = db.query(UserGroupUser).filter(and_(literal_column('user_group_id')==user_group.id, literal_column('user_id')==user.id))
        return q.first()


user_group = CRUDUserGroup(UserGroup)
