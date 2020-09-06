from sqlalchemy.orm import Session

from app.crud.base import CRUDBaseLogging
from app.models.interface import Interface
from app.schemas.interface import InterfaceCreate, InterfaceUpdate


class CRUDInterface(CRUDBaseLogging[Interface, InterfaceCreate, InterfaceUpdate]):
    def get_by_template_table_name(self, db: Session, *, table_name: str) -> Interface:
        query = db.query(Interface).filter(
            Interface.table_template["table_name"].astext == table_name
        )
        return query.first()

    # TODO: Create CRUD to create the templated backing table


interface = CRUDInterface(Interface)
