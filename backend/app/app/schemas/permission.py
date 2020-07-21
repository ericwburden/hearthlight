from enum import Enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ResourceTypeEnum(str, Enum):
    node = "node"


class PermissionTypeEnum(str, Enum):
    create = "create"
    read = "read"
    update = "update"
    delete = "delete"


# Shared properties
class PermissionBase(BaseModel):
    resource_id: Optional[int]
    resource_type: Optional[ResourceTypeEnum]
    permission_type: Optional[PermissionTypeEnum]


# Properties to receive on item creation
class PermissionCreate(PermissionBase):
    resource_id: int
    resource_type: ResourceTypeEnum
    permission_type: PermissionTypeEnum


# Properties to receive on item update
class PermissionUpdate(PermissionBase):
    pass


# Properties shared by models stored in DB
class PermissionInDBBase(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: int
    updated_by_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Permission(PermissionInDBBase):
    pass


# Properties properties stored in DB
class PermissionInDB(PermissionInDBBase):
    pass
