from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# Shared properties
class NodeBase(BaseModel):
    parent_id: Optional[int]
    node_type: Optional[str]
    name: Optional[str]
    is_active: Optional[bool] = True


# Properties to receive on node creation
class NodeCreate(NodeBase):
    node_type: str
    name: str


# Properties to receive on node update
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


class NodeList(BaseModel):
    total_records: int
    nodes: Optional[List[Node]] = []


# Properties properties stored in DB
class NodeInDB(NodeInDBBase):
    pass


class NodeChild(BaseModel):
    node_id: int
    child_type: str
    child_id: int
    child_name: str
