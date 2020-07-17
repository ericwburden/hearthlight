from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models
from app.schemas.network import NetworkCreate
from app.tests.utils.user import create_random_user


def create_random_network(
    db: Session, *, creator_id: Optional[int] = None
) -> models.Network:
    if creator_id is None:
        user = create_random_user(db)
        creator_id = user.id
    network_in = NetworkCreate(created_by_id=creator_id)
    return crud.network.create(db=db, obj_in=network_in)
