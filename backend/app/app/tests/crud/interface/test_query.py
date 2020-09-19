from datetime import timedelta
from sqlalchemy.orm import Session

from app import crud
from app.models.user import User
from app.schemas.interface import QueryCreate, QueryUpdate
from app.tests.utils.interface import test_query_template
from app.tests.utils.utils import random_lower_string


QUERY_INTERFACE_TYPE = "query_interface"

# --------------------------------------------------------------------------------------
# region Tests for basic CRUD fuctions by superuser ------------------------------------
# --------------------------------------------------------------------------------------


def test_create_query(db: Session, superuser: User) -> None:
    name = random_lower_string()
    refresh_interval = timedelta(days=1)
    query_template = test_query_template()
    query_in = QueryCreate(
        name=name, template=query_template, refresh_interval=refresh_interval
    )
    query = crud.query.create(db=db, obj_in=query_in, created_by_id=superuser.id)
    assert query
    assert query.name == name
    assert query.template == query_template
    assert query.interface_type == QUERY_INTERFACE_TYPE
    assert query.refresh_interval == refresh_interval.total_seconds()
    assert query.created_by_id == superuser.id


def test_get_query(db: Session, superuser: User) -> None:
    name = random_lower_string()
    refresh_interval = timedelta(days=1)
    query_template = test_query_template()
    query_in = QueryCreate(
        name=name, template=query_template, refresh_interval=refresh_interval
    )
    query = crud.query.create(db=db, obj_in=query_in, created_by_id=superuser.id)
    stored_query = crud.query.get(db=db, id=query.id)
    assert stored_query
    assert query.name == stored_query.name
    assert query.template == stored_query.template
    assert query.interface_type == QUERY_INTERFACE_TYPE
    assert query.refresh_interval == stored_query.refresh_interval
    assert query.created_by_id == stored_query.created_by_id


def test_get_multi_query(db: Session, superuser: User) -> None:
    names = [random_lower_string() for i in range(10)]
    refresh_interval = timedelta(hours=1)
    query_template = test_query_template()
    new_queries_in = [
        QueryCreate(name=n, template=query_template, refresh_interval=refresh_interval)
        for n in names
    ]
    [
        crud.query.create(db=db, obj_in=query_in, created_by_id=superuser.id)
        for query_in in new_queries_in
    ]
    stored_queries = crud.query.get_multi(db=db)
    for nqi in new_queries_in:
        found_match = False
        for sq in stored_queries:
            name_match = nqi.name == sq.name
            table_template_match = nqi.template == sq.template
            if name_match and table_template_match:
                found_match = True
                break
        assert found_match


def test_update_query(db: Session, superuser: User) -> None:
    name = random_lower_string()
    refresh_interval = timedelta(days=1)
    query_template = test_query_template()
    query_in = QueryCreate(
        name=name, template=query_template, refresh_interval=refresh_interval
    )
    query = crud.query.create(db=db, obj_in=query_in, created_by_id=superuser.id)
    name2 = random_lower_string()
    query_update = QueryUpdate(name=name2)
    updated_query = crud.query.update(
        db=db, db_obj=query, obj_in=query_update, updated_by_id=superuser.id
    )
    assert query.id == updated_query.id
    assert query.name == updated_query.name
    assert query.name == name2
    assert query.updated_by_id == superuser.id


def test_delete_query(db: Session, superuser: User) -> None:
    name = random_lower_string()
    refresh_interval = timedelta(days=1)
    query_template = test_query_template()
    query_in = QueryCreate(
        name=name, template=query_template, refresh_interval=refresh_interval
    )
    query = crud.query.create(db=db, obj_in=query_in, created_by_id=superuser.id)
    query2 = crud.query.remove(db, id=query.id)
    query3 = crud.query.get(db=db, id=query.id)
    assert query3 is None
    assert query2.id == query.id
    assert query2.name == name
    assert query2.created_by_id == superuser.id


def test_run_query(db: Session, superuser: User) -> None:
    name = random_lower_string()
    refresh_interval = timedelta(days=1)
    query_template = {
        "select": {"columns": [{"table": {"name": "query_interface"}, "column": "*"}]}
    }
    query_in = QueryCreate(
        name=name, template=query_template, refresh_interval=refresh_interval
    )
    query = crud.query.create(db=db, obj_in=query_in, created_by_id=superuser.id)
    query_result = crud.query.run_query(db=db, id=query.id)
    db.refresh(query)
    assert query_result
    assert query.last_run
    assert query.last_result


def test_run_query_fetch_last_run(db: Session, superuser: User) -> None:
    name = random_lower_string()
    refresh_interval = timedelta(days=1)
    query_template = {
        "select": {"columns": [{"table": {"name": "query_interface"}, "column": "*"}]}
    }
    query_in = QueryCreate(
        name=name, template=query_template, refresh_interval=refresh_interval
    )
    query = crud.query.create(db=db, obj_in=query_in, created_by_id=superuser.id)
    crud.query.run_query(db=db, id=query.id)
    pre_fetch_last_run = query.last_run
    query_result = crud.query.run_query(db=db, id=query.id)
    db.refresh(query)
    assert query_result
    assert query.last_run == pre_fetch_last_run


def test_run_query_with_error(db: Session, superuser: User) -> None:
    name = random_lower_string()
    refresh_interval = timedelta(days=1)
    query_template = {
        "select": {"columns": [{"table": {"name": "garbage"}, "column": "*"}]}
    }
    query_in = QueryCreate(
        name=name, template=query_template, refresh_interval=refresh_interval
    )
    query = crud.query.create(db=db, obj_in=query_in, created_by_id=superuser.id)
    query_result = crud.query.run_query(db=db, id=query.id)
    db.refresh(query)
    assert query_result
    assert "msg" in query_result[0].keys()
