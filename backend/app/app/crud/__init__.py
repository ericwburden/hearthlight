from .crud_user import user
from .crud_user_group import user_group
from .crud_node import node
from .crud_permission import permission, node_permission
from .crud_interface import interface
from .interfaces import form_input

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
