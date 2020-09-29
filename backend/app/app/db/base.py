# Import all the models, so that Base has them before being
# imported by Alembic. The order of these is important to the
# testing framework. conftest.py imports the models from here
# (in order) and deletes records from the database prior to
# testing. If all models containing a foreign key to a table
# are not deleted before the table referenced, then the pre-testing
# delete operation will fail and records will accumulate in the
# database
from app.db.base_class import Base  # noqa F401
from app.models.user_group import (  # noqa F401
    UserGroupUserRel,
    UserGroupPermissionRel,
    UserGroup,
)
from app.models.user import User  # noqa F401
from app.models.permission import (  # noqa F401
    NodePermission,
    InterfacePermission,
    Permission,
)
from app.models.interface import (  # noqa F401
    FormInputInterface,
    QueryInterface,
    InterfaceNodeRel,
    Interface,
)
from app.models.node import Node  # noqa F401
