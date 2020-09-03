from app.crud.base import CRUDBaseLogging
from app.models.interface import Interface
from app.schemas.interface import InterfaceCreate, InterfaceUpdate


class CRUDInterface(CRUDBaseLogging[Interface, InterfaceCreate, InterfaceUpdate]):
    pass


interface = CRUDInterface(Interface)
