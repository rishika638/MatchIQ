#!/bin/sh
set -e

echo "Running database migrations..."
python scripts/migrate.py

echo "Initializing production seed data..."
python scripts/init_and_seed.py

echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-10000}"
