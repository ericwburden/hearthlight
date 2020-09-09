from fastapi import APIRouter

from app.api.api_v1.endpoints import form_inputs, interfaces, login, nodes, users, user_groups, utils

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(interfaces.router, prefix="/interfaces", tags=["interfaces"])
api_router.include_router(form_inputs.router, prefix="/interfaces", tags=["interfaces", "form inputs"])
api_router.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    user_groups.router, prefix="/user_groups", tags=["user groups"]
)
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
