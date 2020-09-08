from app.crud.base import (
    CRUDInterfaceBase,
    ModelType,
    CreateSchemaType,
    UpdateSchemaType,
)


class CRUDInterfaceFormInput(
    CRUDInterfaceBase[ModelType, CreateSchemaType, UpdateSchemaType]
):
    pass
