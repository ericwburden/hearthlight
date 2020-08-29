from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class UserGroupBase(BaseModel):
    name: Optional[str]
    node_id: Optional[int]


# Properties to receive on item creation
class UserGroupCreate(UserGroupBase):
    node_id: int
    name: str


# Properties to receive on item update
class UserGroupUpdate(UserGroupBase):
    pass


# Properties shared by models stored in DB
class UserGroupInDBBase(UserGroupBase):
    id: int
    node_id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: int
    updated_by_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class UserGroup(UserGroupInDBBase):
    pass


# Properties properties stored in DB
class UserGroupInDB(UserGroupInDBBase):
    pass


class UserGroupUser(BaseModel):
    user_group_id: int
    user_id: int

    class Config:
        orm_mode = True
