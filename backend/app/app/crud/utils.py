from sqlalchemy.orm import Session
from typing import Optional
from fastapi.encoders import jsonable_encoder
from app.db.base_class import Base


def model_encoder(db_obj: Base, db: Optional[Session] = None) -> dict:
    if db:
        db.refresh(db_obj)
    return jsonable_encoder(db_obj)
