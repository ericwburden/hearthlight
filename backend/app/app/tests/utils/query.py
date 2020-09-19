from datetime import timedelta
from random import randint
from sqlalchemy.orm import Session

from app import crud
from app.models import QueryInterface
from app.schemas import QueryCreate
from app.tests.utils.interface import test_query_template
from app.tests.utils.utils import random_lower_string


def create_random_query_interface(db: Session) -> QueryInterface:
    query_template = {
        "select": {"columns": [{"table": {"name": "query_interface"}, "column": "*"}]}
    }
    query_in = QueryCreate(
        name=random_lower_string(),
        template=query_template,
        refresh_interval=timedelta(seconds=randint(36000, 576000)),
    )
    query = crud.query.create(db=db, obj_in=query_in, created_by_id=1)
    return query
