from datetime import datetime, timedelta
from sqlalchemy import MetaData
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm import aliased, Session
from sqlalchemy.orm.query import Query
from typing import Any, Dict, Iterable, List, Optional

from app.crud.base import AccessControl, CRUDBaseLogging
from app.crud.utils import model_encoder
from app.db.base_class import Base
from app.db.session import engine
from app.models.interface import QueryInterface
from app.models.permission import InterfacePermission
from app.schemas.interface import (
    QueryCreate,
    QueryUpdate,
)
from app.schemas.interface.templates import QueryTemplate


class QueryTemplateConverter:
    """Converts QueryTemplate to a SQLAlchemy query
    """

    def __init__(self, base: DeclarativeMeta, engine: Engine):
        self.base = base
        self.metadata = MetaData()
        self.metadata.bind = base
        self.metadata.reflect(bind=engine)

    def _table_items(self, exp: Dict[str, Any]) -> Iterable[Dict[str, str]]:
        """Extracts the table elements from QueryTemplate

        Args:
            exp (Dict[str, Any]): Dict from QueryTemplate

        Returns:
            Iterable[Dict[str, str]]: Generator of table references

        Yields:
            Iterator[Iterable[Dict[str, str]]]: Generator of table
            references
        """
        if hasattr(exp, "items"):
            for k, v in exp.items():
                if k == "table" and v:
                    yield v
                if isinstance(v, dict):
                    for result in self._table_items(v):
                        yield result
                elif isinstance(v, list):
                    for li in v:
                        for result in self._table_items(li):
                            yield result

    def _table_dict(
        self, table_items: List[Dict[str, str]]
    ) -> Dict[str, DeclarativeMeta]:
        """Dict for accessing query tables

        Args:
            table_items (List[Dict[str, str]]): Table references in
            from QueryTemplate, in Dict form

        Returns:
            [Dict[str, DeclarativeMeta]]: Dict of SQLAlchemy tables,
            by name or alias, as appropriate
        """
        tables = {}
        for table_item in table_items:
            table_key = (
                table_item["alias"] if table_item["alias"] else table_item["name"]
            )
            if table_key not in tables.keys():
                table_name = table_item["name"]
                if table_name in self.base.metadata.tables.keys():
                    table = self.base.metadata.tables[table_name]
                else:
                    table = type(
                        table_name,
                        (self.base,),
                        {"__table__": self.metadata.tables[table_name]},
                    )
                if table_item["alias"]:
                    table = aliased(table, name=table_item["alias"])
                tables[table_key] = table
        return tables

    def convert(self, query_schema: QueryTemplate, db: Session) -> Query:
        """Convert the QueryTemplate to a SQLAlchemy Query

        Args:
            query_schema (QueryTemplate): JSON-based schema for the query
            db (Session): SQLALchemy Session

        Returns:
            Query: The generated SQLAlchemy query
        """
        table_items = self._table_items(query_schema.dict())
        tables = self._table_dict(table_items)
        query = db

        select_fields = query_schema.select.items(tables)
        query = query.query(*select_fields)

        if query_schema.joins:
            for join in query_schema.joins:
                conditions = join.conditions(tables)
                query = query.join(join.table(tables), *conditions)

        if query_schema.filters:
            filters = [f(tables) for f in query_schema.filters]
            query = query.filter(*filters)

        if query_schema.group_by:
            group_by_fields = query_schema.group_by.items(tables)
            query = query.group_by(*group_by_fields)

        return query


class CRUDQueryInterface(
    AccessControl[QueryInterface, InterfacePermission],
    CRUDBaseLogging[QueryInterface, QueryCreate, QueryUpdate],
):
    def run_query(
        self,
        db: Session,
        id: int,
        page: Optional[int] = 0,
        page_size: Optional[int] = 25,
    ) -> List[Dict[str, Any]]:
        query = db.query(self.model).get(id)
        if query.last_run:
            query_expires = query.last_run + timedelta(seconds=query.refresh_interval)
            if datetime.now() <= query_expires:
                return query.last_result
        template = QueryTemplate(**query.template)
        query_converter = QueryTemplateConverter(Base, engine)
        query_query = query_converter.convert(template, db)
        query.total_rows = query_query.count()
        query.last_page = page
        query.last_page_size = page_size
        result = [
            model_encoder(q)
            for q in query_query.limit(page_size).offset(page * page_size).all()
        ]
        query.last_run = datetime.now()
        query.last_result = result
        db.commit()
        return result


query = CRUDQueryInterface(QueryInterface, InterfacePermission)
