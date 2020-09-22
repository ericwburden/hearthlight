#! /usr/bin/env bash

# Let the DB start
python /app/app/backend_pre_start.py

# To retain alembic migrations between restarts, comment the
# two lines below
rm -f /app/alembic/versions/*.py
alembic revision --autogenerate -m "First Revision"

# Run migrations
alembic upgrade head

# Create initial data in DB
python /app/app/initial_data.py
