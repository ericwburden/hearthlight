#! /usr/bin/env bash

# Let the DB start
python /app/app/backend_pre_start.py

# To start fresh with a single revision, delete the .py files in
# app/alembic/versions, drop the database, and uncomment the 
# line below for a single run. After that, comment it back.
# alembic revision --autogenerate -m "First Revision"

# Run migrations
alembic upgrade head

# Create initial data in DB
python /app/app/initial_data.py
