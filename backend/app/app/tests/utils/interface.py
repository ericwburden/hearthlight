from typing import Optional
from sqlalchemy.orm import Session

from app import crud
from app.models import Interface
from app.schemas import (
    InterfaceCreate,
    InterfaceTemplate,
    TableTemplate,
    ColumnTemplate,
    QueryTemplate,
)
from app.tests.utils.utils import random_lower_string


def test_table_template(name: Optional[str] = None) -> TableTemplate:
    if not name:
        name = random_lower_string()
    return TableTemplate(
        table_name=name,
        columns=[
            ColumnTemplate(
                column_name="id",
                data_type="Integer",
                kwargs={"primary_key": True, "index": True},
            )
        ],
    )


def test_query_template() -> QueryTemplate:
    test_query = {
        "select": {
            "columns": [
                {"table": {"name": "user", "alias": "monkey"}, "column": "full_name"},
                {"table": {"name": "user", "alias": "monkey"}, "column": "email"},
            ],
            "calculated_columns": [
                {
                    "func": "count",
                    "args": [{"type": "scalar", "value": 1}],
                    "label": "num_groups",
                }
            ],
        },
        "joins": [
            {
                "table": {"name": "user_group_user_rel", "alias": None},
                "by": [
                    {
                        "left": {
                            "type": "column",
                            "table": {"name": "user", "alias": "monkey"},
                            "value": "id",
                        },
                        "comparator": "==",
                        "right": {
                            "type": "column",
                            "table": {"name": "user_group_user_rel", "alias": None},
                            "value": "user_id",
                        },
                    },
                ],
            },
            {
                "table": {"name": "user_group", "alias": None},
                "by": [
                    {
                        "left": {
                            "type": "column",
                            "table": {"name": "user_group_user_rel"},
                            "value": "user_group_id",
                        },
                        "comparator": "==",
                        "right": {
                            "type": "column",
                            "table": {"name": "user_group", "alias": None},
                            "value": "id",
                        },
                    },
                ],
            },
        ],
        "filters": [
            {
                "type": "and",
                "filters": [
                    {
                        "left": {
                            "type": "column",
                            "table": {"name": "user", "alias": "monkey"},
                            "value": "id",
                        },
                        "comparator": ">",
                        "right": {"type": "scalar", "value": 1},
                    },
                ],
            },
        ],
        "group_by": {
            "columns": [
                {"table": {"name": "user", "alias": "monkey"}, "column": "full_name"},
                {"table": {"name": "user", "alias": "monkey"}, "column": "email"},
            ]
        },
    }
    return QueryTemplate(**test_query)


def create_random_interface(db: Session, table_name: Optional[str] = None) -> Interface:
    interface_in = InterfaceCreate(
        name=random_lower_string(),
        interface_type="test",
        template=InterfaceTemplate(table=test_table_template(name=table_name)),
    )
    interface = crud.interface.create(db, obj_in=interface_in, created_by_id=1)
    return interface
