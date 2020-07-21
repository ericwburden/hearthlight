import re
from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    pass


class Default:
    id: Any
    __name__: str
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str: # noqa
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
