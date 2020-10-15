from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic.networks import EmailStr
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app import models, schemas, crud
from app.api import deps
from app.core.celery_app import celery_app
from app.db.session import engine
from app.utils import send_test_email

router = APIRouter()


@router.post("/test-celery/", response_model=schemas.Msg, status_code=201)
def test_celery(
    msg: schemas.Msg,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test Celery worker.
    """
    celery_app.send_task("app.worker.test_celery", args=[msg.msg])
    return {"msg": "Word received"}


@router.post("/test-email/", response_model=schemas.Msg, status_code=201)
def test_email(
    email_to: EmailStr,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}


@router.get("/node-types/", response_model=List[str], status_code=200)
def get_node_types(db: Session = Depends(deps.get_db)) -> List[str]:
    return crud.node.get_types(db)


@router.get("/table-names/", response_model=List[str], status_code=200)
def get_node_types() -> List[str]:
    inspector = inspect(engine)
    return inspector.get_table_names()


@router.get("/column-names/{table_name}", response_model=List[str], status_code=200)
def get_node_types(table_name: str) -> List[str]:
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        raise HTTPException(status_code=404, detail=f"No table named {table_name}.")
    columns = inspector.get_columns(table_name)
    return [c.get("name") for c in columns]
