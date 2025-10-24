#!/usr/bin/env bash
set -e

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting app with Gunicorn..."
gunicorn main:app -k uvicorn.workers.UvicornWorker
