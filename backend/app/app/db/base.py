# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa F401
from app.models.node import Node  # noqa F401
from app.models.user import User  # noqa F401
from app.models.user_group import (  # noqa F401
    UserGroup,  # noqa F401
    UserGroupUserRel,  # noqa F401
    UserGroupPermissionRel,  # noqa F401
)
from app.models.permission import Permission, NodePermission  # noqa F401
from app.models.interface import Interface  # noqa F401
