from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ColumnTemplate(BaseModel):
    column_name: str
    data_type: str
    args: Optional[List[Any]] = None
    kwargs: Optional[Dict[str, Any]] = None


class TableTemplate(BaseModel):
    table_name: str
    columns: List[ColumnTemplate]
