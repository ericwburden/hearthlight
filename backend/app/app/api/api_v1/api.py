from fastapi import APIRouter

from app.api.api_v1.endpoints import interfaces, login, nodes, user_groups, users, utils

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(
    interfaces.interface_router,
    prefix="/interfaces",
    tags=["interfaces"],
)
api_router.include_router(
    interfaces.form_input_router,
    prefix="/interfaces/form-inputs",
    tags=["interfaces", "form inputs"],
)
api_router.include_router(
    interfaces.form_input_entry_router,
    prefix="/interfaces/form-inputs",
    tags=["interfaces", "form inputs"],
)
api_router.include_router(
    interfaces.query_router,
    prefix="/interfaces/queries",
    tags=["interfaces", "queries"],
)
api_router.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    user_groups.router, prefix="/user_groups", tags=["user groups"]
)
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
