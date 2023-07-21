#!/bin/sh
docker exec main_db psql -U user -d postgres -c "DROP DATABASE db;"
docker exec main_db psql -U user -d postgres -c "CREATE DATABASE db;"
alembic upgrade head