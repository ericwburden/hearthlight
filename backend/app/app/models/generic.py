from sqlalchemy import MetaData
from app.db.session import engine
from app.db.base_class import Base


def get_generic_model(table_name: str) -> Base:
    metadata = MetaData(engine, reflect=True)
    return type(table_name, (Base,), {"__table__": metadata.tables[table_name]})
