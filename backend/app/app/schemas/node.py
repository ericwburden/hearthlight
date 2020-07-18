from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class NodeBase(BaseModel):
    parent_id: Optional[int]
    node_type: str
    name: str
    is_active: bool = True


# Properties to receive on item creation
class NodeCreate(NodeBase):
    pass


# Properties to receive on item update
class NodeUpdate(NodeBase):
    pass


# Properties shared by models stored in DB
class NodeInDBBase(NodeBase):
    id: int
    depth: int
    created_at: datetime
    updated_at: datetime
    created_by_id: int
    updated_by_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Node(NodeInDBBase):
    pass


# Properties properties stored in DB
class NodeInDB(NodeInDBBase):
    pass
