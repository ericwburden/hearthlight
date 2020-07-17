from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class NetworkBase(BaseModel):
    name: str
    is_active: bool = True


# Properties to receive on item creation
class NetworkCreate(NetworkBase):
    pass


# Properties to receive on item update
class NetworkUpdate(NetworkBase):
    pass


# Properties shared by models stored in DB
class NetworkInDBBase(NetworkBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: int
    updated_by_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Network(NetworkInDBBase):
    pass


# Properties properties stored in DB
class NetworkInDB(NetworkInDBBase):
    pass
