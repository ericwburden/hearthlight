from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class InterfaceTypeEnum(str, Enum):
    test = "test"
    form_input = "form_input"


class ColumnTemplate(BaseModel):
    column_name: str
    data_type: str
    kwargs: Dict[str, Any]


class TableTemplate(BaseModel):
    table_name: str
    columns: List[ColumnTemplate]


# Shared properties
class InterfaceBase(BaseModel):
    name: Optional[str]
    interface_type: Optional[InterfaceTypeEnum]
    table_template: Optional[TableTemplate]
    ui_template: Optional[Dict[str, Any]]


# Properties to receive on node creation
class InterfaceCreate(InterfaceBase):
    name: str
    interface_type: InterfaceTypeEnum
    table_template: TableTemplate


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
