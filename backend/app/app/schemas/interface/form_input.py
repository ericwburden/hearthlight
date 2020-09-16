from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from .templates import TableTemplate


# Shared properties
class FormInputBase(BaseModel):
    name: Optional[str]
    template: Optional[TableTemplate]


# Properties to receive on node creation
class FormInputCreate(FormInputBase):
    name: str
    template: TableTemplate


# Properties to receive on node update
class FormInputUpdate(FormInputBase):
    pass


# Properties shared by models stored in DB
class FormInputInDBBase(FormInputBase):
    id: int
    interface_type: str = "form_input"
    table_created: bool = False
    created_at: datetime
    updated_at: datetime
    created_by_id: int
    updated_by_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class FormInput(FormInputInDBBase):
    pass


# Properties properties stored in DB
class FormInputInDB(FormInputInDBBase):
    pass
