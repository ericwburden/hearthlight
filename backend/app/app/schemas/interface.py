from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Json


# Shared properties
class InterfaceBase(BaseModel):
    name: Optional[str]
    interface_type: Optional[str]
    table_template: Optional[Json]
    ui_template: Optional[Json]


# Properties to receive on node creation
class InterfaceCreate(InterfaceBase):
    name: str
    interface_type: str
    table_template: Json


# Properties to receive on node update
class InterfaceUpdate(InterfaceBase):
    pass


# Properties shared by models stored in DB
class InterfaceInDBBase(InterfaceBase):
    id: int
    table_created: bool = False
    created_at: datetime
    updated_at: datetime
    created_by_id: int
    updated_by_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Interface(InterfaceInDBBase):
    pass


# Properties properties stored in DB
class InterfaceInDB(InterfaceInDBBase):
    pass
