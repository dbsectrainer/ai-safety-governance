#!/bin/bash
set -e

# Function to check if PostgreSQL is ready
postgres_ready() {
    python << END
import sys
import psycopg2
try:
    psycopg2.connect(
        dbname="${POSTGRES_DB:-ai_safety_governance}",
        user="${POSTGRES_USER:-postgres}",
        password="${POSTGRES_PASSWORD:-postgres}",
        host="${POSTGRES_HOST:-db}",
        port="${POSTGRES_PORT:-5432}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

# Wait for PostgreSQL to be ready
until postgres_ready; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - handling migrations"

# Stamp the current migration without running it, then try to upgrade
alembic stamp head || true
alembic upgrade head || true

# Start the FastAPI application with uvicorn worker
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 60 --access-logfile - --error-logfile - src.main:app
