#!/bin/sh
alembic upgrade head

/bin/sh /start-reload.sh
