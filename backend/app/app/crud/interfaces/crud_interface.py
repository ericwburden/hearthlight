from app.crud.base import (
    AccessControl,
    CRUDBaseLogging,
    CreateSchemaType,
    UpdateSchemaType,
)
from app.models.interface import Interface
from app.models.permission import InterfacePermission


class CRUDInterface(
    AccessControl[Interface, InterfacePermission],
    CRUDBaseLogging[Interface, CreateSchemaType, UpdateSchemaType],
):
    """CRUD class for generic interfaces

    This is mostly to allow fetching of generic interface records. The
    create and update methods have been disabled.
    """

    def create(self, *args, **kwargs) -> None:
        pass

    def update(self, *args, **kwargs) -> None:
        pass


interface = CRUDInterface(Interface, InterfacePermission)
