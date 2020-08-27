from typing import Any
from fastapi.encoders import jsonable_encoder
from app.db.base_class import Base

def model_encoder(db_obj: Any) -> dict:
    obj_data = db_obj
    if isinstance(db_obj, Base):
        obj_data = {
            col.name: getattr(db_obj, col.name) for col in db_obj.__table__.columns
        }
    return jsonable_encoder(obj_data)