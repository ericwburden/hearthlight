from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBaseLogging
from app.models.network import Network
from app.schemas.network import NetworkCreate, NetworkUpdate


class CRUDNetwork(CRUDBaseLogging[Network, NetworkCreate, NetworkUpdate]):
    pass


network = CRUDNetwork(Network)
