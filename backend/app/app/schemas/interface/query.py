from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from pydantic import BaseModel
from .templates import QueryTemplate


# Shared properties
class QueryBase(BaseModel):
    name: Optional[str]
    template: Optional[QueryTemplate]
    refresh_interval: Optional[timedelta]


# Properties to receive on creation
class QueryCreate(QueryBase):
    name: str
    template: QueryTemplate
    refresh_interval: Optional[timedelta] = timedelta(hours=1)


# Properties to receive on update
class QueryUpdate(QueryBase):
    pass


# Properties shared by models stored in DB
class QueryInDBBase(QueryBase):
    id: int
    interface_type: str = "query_interface"
    last_run: Optional[datetime] = None
    result_expires: Optional[datetime] = 86400
    last_result: Optional[List[Dict[str, Any]]]
    last_page: int
    last_page_size: int
    total_rows: int
    created_at: datetime
    updated_at: datetime
    created_by_id: int
    updated_by_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Query(QueryInDBBase):
    pass


# Properties properties stored in DB
class QueryInDB(QueryInDBBase):
    pass
