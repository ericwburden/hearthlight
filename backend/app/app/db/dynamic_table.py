import json
from typing import Any, Tuple, Dict
from sqlalchemy import Column
from app.db.base import Base


# This is a test json definition for a SQLAlchemy table
test_table_definition = """{
    "table_name": "TestingTable",
    "columns": [
        {
            "column_name": "id",
            "data_type": "Integer",
            "kwargs": {
                "primary_key": true,
                "index": true
            }
        },
        {
            "column_name": "value",
            "data_type": "Integer",
            "kwargs": {
                "nullable": true
            }
        },
        {
            "column_name": "name",
            "data_type": "String(256)",
            "kwargs": {}
        }
    ]
}"""

def json_to_table_def(json_string: str, base_class: Tuple[Any]) -> Base:
    """Convert a JSON schema into a SQLAlchemy table

    The JSON schema should be in the form of:
    {
        "table_name": "CamelCase",
        "columns": [
            "column_name": "snake_case",
            "data_type": "String, Integer, Boolean, etc.",
            "kwargs": {
                "arg_name": "value"
            }
        ]
    }

    The "data_type" should be a string representing a valid SQLAlchemy
    data type such as String(256), Integer, Boolean, etc. The "kwargs"
    are a dict of addtional arguments to pass to Column(), such as 
    primary_key, nullable, index, etc.

    Args:
        json_string (str): JSON template
        base_class (Tuple[Any]): The abstract table class to subclass
        the new table from

    Returns:
        Base: A SQLAlchemy Table model
    """
    base_class = base_class
    json_obj = json.loads(json_string)
    table_name = json_obj["table_name"]
    columns = {c["column_name"]:dict_to_column_def(c) for c in json_obj["columns"]}
    return type(table_name, base_class, columns)

def dict_to_column_def(column_dict: Dict[str, str]) -> Column:
    """Given a column def dictionary, return a Column

    Args:
        column_dict (Dict[str, str]): A dictionary from 
        json_to_table_def()

    Returns:
        Column: The Column
    """
    data_type = column_dict["data_type"]
    kwargs_str = ", ".join([f"{k}={v}" for k,v in column_dict['kwargs'].items()])
    column_str = f"Column({data_type}, {kwargs_str})"
    return eval(column_str)