import operator

from sqlalchemy import MetaData, and_, or_
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm import aliased, Session
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import text
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.sql.schema import MetaData
from typing import List, Any, Dict, Union, Callable, Iterable

from app.db.session import engine, SessionLocal
from app.db.base_class import Base


metadata = MetaData()
metadata.bind = Base
metadata.reflect(bind=engine)
db = SessionLocal()

test_query = {
    "select": {
        "table": {"name": "user", "alias": "monkey"},
        "fields": ["id", "full_name", "email"],
    },
    "filter": [
        {
            "type": "or",
            "filters": [
                {
                    "left": {
                        "type": "column",
                        "table": {"name": "user", "alias": "monkey"},
                        "value": "id",
                    },
                    "comparator": "==",
                    "right": {"type": "scalar", "value": 1},
                },
                {
                    "left": {
                        "type": "column",
                        "table": {"name": "user", "alias": "monkey"},
                        "value": "id",
                    },
                    "comparator": "==",
                    "right": {"type": "scalar", "value": 1},
                },
            ],
        },
        {
            "left": {
                "type": "column",
                "table": {"name": "user", "alias": "monkey"},
                "value": "id",
            },
            "comparator": "in",
            "right": {"type": "list", "value": [1, 1, 1]},
        },
    ],
    "join": {
        "table": {"name": "user_group_user_rel", "alias": None},
        "fields": None,
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
}


class SelectClause:
    def __init__(self, clause: Dict[str, Any], tables: Dict[str, DeclarativeMeta]):
        table_item = clause["table"]
        table_name = table_item["alias"] if table_item["alias"] else table_item["name"]
        self.field_names = clause.get("fields")
        self.table = tables[table_name]

    def fields(self) -> List[Union[DeclarativeMeta, InstrumentedAttribute]]:
        if not self.field_names:
            return [self.table]
        return [getattr(self.table, field) for field in self.field_names]


class JoinClause:
    def __init__(self, clause: Dict[str, Any], tables: Dict[str, DeclarativeMeta]):
        table_item = clause["table"]
        table_name = table_item["alias"] if table_item["alias"] else table_item["name"]
        self.field_names = clause.get("fields")
        self.table = tables[table_name]
        self.comparisons = clause.get("by")
        self.tables = tables

    def fields(self) -> List[Union[DeclarativeMeta, InstrumentedAttribute]]:
        if not self.field_names:
            return [self.table]
        return [getattr(self.table, field) for field in self.field_names]

    def join_conditions(self) -> BooleanClauseList:
        boolean_clauses = [BooleanClause(c, self.tables) for c in self.comparisons]
        return [bc.boolean_clause_list() for bc in boolean_clauses]


class BooleanClause:
    def __init__(self, clause: Dict[str, Any], tables: Dict[str, DeclarativeMeta]):
        if set(clause.keys()) == {"left", "comparator", "right"}:
            self.clause_type = "single"
            self.filter_expressions = [BooleanExpression.from_dict(clause, tables)]
            return
        if set(clause.keys()) == {"type", "filters"}:
            self.clause_type = clause.get("type")
            self.filter_expressions = [
                BooleanExpression.from_dict(f, tables) for f in clause.get("filters")
            ]
            return

        raise ValueError(
            "Filter clause not in the correct format, please refer "
            "to documentation for class: FilterClause"
        )

    def boolean_clause_list(self) -> BooleanClauseList:
        binary_expressions = [fe.binary_expression() for fe in self.filter_expressions]
        if self.clause_type == "and":
            return and_(*binary_expressions)
        if self.clause_type == "or":
            return or_(*binary_expressions)
        if self.clause_type == "single":
            return binary_expressions[0]


class BooleanExpression:
    @staticmethod
    def _in(left: [Any], right: List[Any]) -> bool:
        return left.in_(right)

    @staticmethod
    def _not_in(left: [Any], right: List[Any]) -> bool:
        return left.not_in_(right)

    @staticmethod
    def _like(left: [Any], right: List[Any]) -> bool:
        return left.like(right)

    @staticmethod
    def _not_like(left: [Any], right: List[Any]) -> bool:
        return left.notlike(right)

    @staticmethod
    def operation(op_string) -> Callable:
        operations = {
            "=": operator.eq,
            "==": operator.eq,
            "<>": operator.ne,
            "!=": operator.ne,
            ">": operator.gt,
            ">=": operator.ge,
            "<": operator.lt,
            "<=": operator.le,
            "in": BooleanExpression._in,
            "not in": BooleanExpression._not_in,
            "like": BooleanExpression._like,
            "not like": BooleanExpression._not_like,
        }
        return operations[op_string]

    @staticmethod
    def evaluate_comparand(
        comparand: Dict[str, Any], tables: Dict[str, DeclarativeMeta]
    ) -> Any:
        if comparand.get("type") == "column":
            table_item = comparand["table"]
            table_name = (
                table_item["alias"] if table_item["alias"] else table_item["name"]
            )
            column = comparand["value"]
            return getattr(tables[table_name], column)
        return comparand["value"]

    def __init__(
        self,
        left: Dict[str, str],
        right: Dict[str, str],
        comparator: str,
        tables: Dict[str, DeclarativeMeta],
    ):
        if not left.get("type") == "column":
            raise TypeError("The left-hand side of the comparison should be a column")
        self.left = BooleanExpression.evaluate_comparand(left, tables)
        self.right = BooleanExpression.evaluate_comparand(right, tables)
        self.comparator = comparator

    @classmethod
    def from_dict(cls, comparison: Dict[str, Any], tables: Dict[str, DeclarativeMeta]):
        left = comparison["left"]
        right = comparison["right"]
        comparator = comparison["comparator"]
        return cls(left, right, comparator, tables)

    def binary_expression(self) -> Union[BinaryExpression, bool]:
        try:
            return BooleanExpression.operation(self.comparator)(self.left, self.right)
        except TypeError as e:
            msg = (
                f"Attempting the comparison: "
                f"({self.left} {self.comparator} {self.right})"
                f" raised the following error: {e}"
            )
            raise TypeError(msg)


class JSONQueryConverter:
    def __init__(self, base: DeclarativeMeta, engine: Engine, db: Session):
        self.metadata = MetaData()
        self.base = base
        self.metadata.bind = base
        self.metadata.reflect(bind=engine)
        self.query = db
        self.tables = dict()

    def _table_items(self, exp: Dict[str, Any]) -> Iterable[Dict[str, str]]:
        if hasattr(exp, "items"):
            for k, v in exp.items():
                if k == "table":
                    yield v
                if isinstance(v, dict):
                    for result in self._table_items(v):
                        yield result
                elif isinstance(v, list):
                    for li in v:
                        for result in self._table_items(li):
                            yield result

    def _build_table_dict(
        self, table_items: List[Dict[str, str]], metadata: MetaData
    ) -> None:
        for table_item in table_items:
            table_key = (
                table_item["alias"] if table_item["alias"] else table_item["name"]
            )
            if table_key not in self.tables.keys():
                table_name = table_item["name"]
                table = type(
                    table_name,
                    (self.base,),
                    {"__table__": self.metadata.tables[table_name]},
                )
                if table_item["alias"]:
                    table = aliased(table, name=table_item["alias"])
                self.tables[table_key] = table

    def convert(self, exp: Dict[str, Any]):
        table_items = self._table_items(exp)
        self._build_table_dict(table_items, self.metadata)
        for k, v in exp.items():
            if k == "select":
                fields = SelectClause(v, self.tables).fields()
                self.query = self.query.query(*fields)
            if k == "filter":
                filters = [
                    BooleanClause(c, self.tables).boolean_clause_list() for c in v
                ]
                self.query = self.query.filter(*filters)
            if k == "join":
                join_clause = JoinClause(v, self.tables)
                self.query = self.query.join(
                    *join_clause.fields(), *join_clause.join_conditions()
                )
        return self.query


def start(query_dict):
    converter = JSONQueryConverter(Base, engine, SessionLocal())
    return converter.convert(query_dict)
