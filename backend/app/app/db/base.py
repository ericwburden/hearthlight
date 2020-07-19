# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.item import Item  # noqa
from app.models.node import Node  # noqa
from app.models.user import User  # noqa
from app.models.user_group import UserGroup # noqa
from app.models.user_group import UserGroupUser # noqa
