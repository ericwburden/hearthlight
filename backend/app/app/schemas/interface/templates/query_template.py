from __future__ import annotations
import operator

from pydantic import BaseModel, validator
from sqlalchemy import and_, or_, func
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import BooleanClauseList, Label
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.sql.functions import Function
from typing import Any, Optional, Dict, List, Callable, Union


class TableReference(BaseModel):
    """Encodes a reference to a table in the database

    If using the same table multiple times, as in self-referencing
    joins, provide an alias.

    Fields:
        - name (str): The name of the table
        - alias (str): Alias referring to the named table
    """

    name: str
    alias: Optional[str] = None

    def __call__(self, tables: Dict[str, DeclarativeMeta]) -> DeclarativeMeta:
        """Get the table reference, either the alias or the name

        Args:
            tables (Dict[str, DeclarativeMeta]): Dict of database tables
            by reference

        Returns:
            Union[AliasedClass, DeclarativeMeta]: The table referenced
            by this object.
        """
        return tables[self.alias if self.alias else self.name]


class Argument(BaseModel):
    """Represents an argument to a function

    Represents an argument to a function, such as for a calculated
    column or when making a comparison in a filter or a join.

    Fields:
        - type: str - The type of the argument, one of "scalar", "list",
        or "column". "column" should be used when referring to a column
        in a database table.
        - table: Optional[TableReferece] - Required when the type is
        "column", indicates the table housing the referenced column.
        - value: Any: The value of the argument. When the type is
        "column", should be string naming the column to use.
    """

    type: str
    table: Optional[TableReference] = None
    value: Any

    def __call__(self, tables: Dict[str, DeclarativeMeta]) -> Any:
        """Evaluate the argument

        Returns the value directly for "scalar" and "list" types,
        returns a reference to the table column for "column" types.

        Args:
            tables (Dict[str, DeclarativeMeta]): Dict of database tables
            by reference

        Returns:
            Any: The evaluated value of the argument
        """
        if self.type == "column" and self.table:
            return getattr(self.table(tables), self.value)
        return self.value


class Comparison(BaseModel):
    """Represents a comparison operation

    Takes a left-hand side, right-hand side, and comparison operation
    and returns the evaluated comparison for use in filter clauses and
    join operations. Supports the following comparison operators:

    - =
    - ==
    - <>
    - !=
    - >
    - >=
    - <
    - <=
    - in
    - not in
    - like
    - not like

    Fields:
        - left: Argument - The left-hand side of the comparison. Should
        alqways be a column reference.
        - comparator: str - String representing the comparison operation
        - right: Argument - The right-hand side of the comparison
    """

    left: Argument
    comparator: str
    right: Argument

    @staticmethod
    def _in(left: Any, right: List[Any]) -> bool:
        return left.in_(right)

    @staticmethod
    def _not_in(left: Any, right: List[Any]) -> bool:
        return left.not_in_(right)

    @staticmethod
    def _like(left: Any, right: List[Any]) -> bool:
        return left.like(right)

    @staticmethod
    def _not_like(left: Any, right: List[Any]) -> bool:
        return left.notlike(right)

    @staticmethod
    def operations() -> Dict[str, Callable]:
        return {
            "=": operator.eq,
            "==": operator.eq,
            "<>": operator.ne,
            "!=": operator.ne,
            ">": operator.gt,
            ">=": operator.ge,
            "<": operator.lt,
            "<=": operator.le,
            "in": Comparison._in,
            "not in": Comparison._not_in,
            "like": Comparison._like,
            "not like": Comparison._not_like,
        }

    @validator("left")
    def left_must_be_column_type(cls, v):  # noqa
        if v.type != "column":
            raise ValueError("The left-hand side must be a 'column' type")
        return v

    @validator("comparator")
    def comparator_must_be_defined(cls, v):  # noqa
        if v not in Comparison.operations().keys():
            raise ValueError(f"The comparison operator '{v}' is not defined.")
        return v

    def __call__(self, tables: Dict[str, DeclarativeMeta]) -> BinaryExpression:
        """Make the comparison and return the result

        Args:
            tables (Dict[str, DeclarativeMeta]): Dict of database tables
            by reference

        Raises:
            TypeError: When the comparison evaluation returns an error

        Returns:
            BinaryExpression: The evaluation result
        """
        left = self.left(tables)
        right = self.right(tables)
        operation = Comparison.operations()[self.comparator]
        try:
            return operation(left, right)
        except TypeError as e:
            msg = (
                f"Attempting the comparison: "
                f"({left} {self.comparator} {right})"
                f" raised the following error: {e}"
            )
            raise TypeError(msg)


class FilterClause(BaseModel):
    """Represents a set of filter statements

    The filters in a FilterClause may have either an AND or OR
    relationship, depending on the type. Complex filtering can be
    created by mixing nested FilterClauses and Comparisons.

    Fields:
        - type: str - Must be either "and" or "or", representing the
        relationship between the child FilterClauses or Comparisons
    """

    type: str
    filters: List[Union[FilterClause, Comparison]]

    @validator("type")
    def type_must_be_and_or(cls, v):  # noqa
        if v not in ["and", "or"]:
            raise ValueError("The filter clause type must be 'and' or 'or'.")
        return v

    def __call__(self, tables: Dict[str, DeclarativeMeta]) -> BooleanClauseList:
        """Evaluate the FilterClause

        Args:
            tables (Dict[str, DeclarativeMeta]): Dict of database tables
            by reference

        Returns:
            BooleanClauseList: A SQLAlchemy object representing a complex
            set of comparisons
        """
        expressions = [f(tables) for f in self.filters]
        if self.type == "or":
            return or_(*expressions)
        return and_(*expressions)


class CalculatedColumn(BaseModel):
    """Represents a calculated column for a select statement

    Takes advantage of SQLAlchemy's 'func' to generate functions for
    SQL select statements.
    https://docs.sqlalchemy.org/en/13/core/sqlelement.html#sqlalchemy.sql.expression.func

    Fields:
        - func: str - String representing the function to call, such as
        'count', 'concat', 'sum', 'max', etc.
        - args: Optional[List[Argument]] - Optional list of arguments to
        pass to the function, if it takes them.
        - label: Optional[str]: Optional label for the calculated
        column, assigned as the column name.
    """

    func: str
    args: Optional[List[Argument]] = []
    label: Optional[str] = None

    def __call__(self, tables: Dict[str, DeclarativeMeta]) -> Union[Function, Label]:
        """Evaluate the CalculatedColumn

        Args:
            tables (Dict[str, DeclarativeMeta]): Dict of database tables
            by reference

        Returns:
            Union[Function, Label]: The evaluated column, with or
            without a label.
        """
        arg_values = [arg(tables) for arg in self.args]
        dynamic_func = getattr(func, self.func)
        if self.label:
            return dynamic_func(*arg_values).label(self.label)
        return dynamic_func(*arg_values)


class TableColumn(BaseModel):
    """Represents a reference to a database table column

    Fields:
        - table: TableReference - Reference to a database table
        - column: str - Name of the table column
    """

    table: TableReference
    column: str

    def __call__(
        self, tables: Dict[str, DeclarativeMeta]
    ) -> Union[DeclarativeMeta, InstrumentedAttribute]:
        """Evaluate the TableColumn

        Args:
            tables (Dict[str, DeclarativeMeta]): Dict of database tables
            by reference

        Returns:
            Union[DeclarativeMeta, InstrumentedAttribute]: Either the
            table column, or all columns if 'column' == '*'.
        """
        if self.column == "*":
            return self.table(tables)
        return getattr(self.table(tables), self.column)


class SelectClause(BaseModel):
    """Represents a SQL select statement

    Fields:
        - columns: Optional[List[TableColumn]] - List of table column
        references
        - calculated_columns: Optional[List[CalculatedColumn]] - List
        of calculated table columns
    """

    columns: Optional[List[TableColumn]] = []
    calculated_columns: Optional[List[CalculatedColumn]] = []

    def items(
        self, tables: Dict[str, DeclarativeMeta]
    ) -> List[Union[InstrumentedAttribute, Label, Function]]:
        """Evaluate and return all columns

        Args:
            tables (Dict[str, DeclarativeMeta]): Dict of database tables
            by reference

        Returns:
            List[Union[InstrumentedAttribute, Label, Function]]: List of
            evaluated columns to be passed to query()
        """
        columns = [column(tables) for column in self.columns]
        calculated_columns = [cc(tables) for cc in self.calculated_columns]
        return [*columns, *calculated_columns]


class JoinClause(BaseModel):
    """Represents the arguments for a join statement

    Fields:
        - table: TableReference - The table being joined to the query
        - by: List[Comparison] - List of join conditions
    """

    table: TableReference
    by: List[Comparison]

    def conditions(self, tables: Dict[str, DeclarativeMeta]) -> List[BooleanClauseList]:
        """Return a list of evaluated join conditions

        Args:
            tables (Dict[str, DeclarativeMeta]): Dict of database tables
            by reference

        Returns:
            List[BooleanClauseList]: A list of join conditions
        """
        return [c.__call__(tables) for c in self.by]


class GroupByClause(BaseModel):
    """Represents the arguments to a group_by clause

    Fields:
        - columns: List[TableColumn] - List of columns to group the
        resulting query by
    """

    columns: List[TableColumn]

    def items(
        self, tables: Dict[str, DeclarativeMeta]
    ) -> List[Union[DeclarativeMeta, InstrumentedAttribute]]:
        """Evaluated list of columns

        Args:
            tables (Dict[str, DeclarativeMeta]): Dict of database tables
            by reference

        Returns:
            List[Union[DeclarativeMeta, InstrumentedAttribute]]: List
            of evaluated columns
        """
        return [column(tables) for column in self.columns]


class QueryTemplate(BaseModel):
    """Full query template

    Fields:
        - select: SelectClause - Mapping for the select clause
        - joins: Optional[List[JoinClause]] - Mapping for join clauses
        - filters: Optional[List[FilterClause]] - Mapping for items
        to pass to the filter function
        - group_by: Optional[GroupByClause] - Mapping for the group_by
        clause
    """

    select: SelectClause
    joins: Optional[List[JoinClause]] = None
    filters: Optional[List[FilterClause]] = None
    group_by: Optional[GroupByClause] = None


# Needed to allow FilterClauses to be nested
# https://pydantic-docs.helpmanual.io/usage/postponed_annotations/#self-referencing-models
FilterClause.update_forward_refs()
