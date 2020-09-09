from sqlalchemy import MetaData
from app.db.session import engine
from app.db.base_class import Base


def get_generic_model(table_name: str) -> Base:
    if Base._decl_class_registry.get(table_name):
        return Base._decl_class_registry.get(table_name)
    metadata = MetaData()
    metadata.bind = Base
    metadata.reflect(bind=engine)
    return type(table_name, (Base,), {"__table__": metadata.tables[table_name]})
