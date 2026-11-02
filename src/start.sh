#!/bin/bash
set -euo pipefail

cd /app

>&2 echo "Waiting for the database to become available..."
attempt=0
until python - <<'PY'
import sys
from sqlalchemy import create_engine, text

from src.database import get_database_url

try:
    engine = create_engine(get_database_url(), pool_pre_ping=True)
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
except Exception as exc:  # pragma: no cover - container startup path
    print(f"database not ready: {exc}", file=sys.stderr)
    sys.exit(1)
PY
do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 60 ]; then
    >&2 echo "Database did not become available within 60 seconds."
    exit 1
  fi
  sleep 1
done

>&2 echo "Database is available. Applying migrations..."
alembic upgrade head

# Schema setup is handled above; skip duplicate per-worker initialisation.
export DB_AUTO_INIT="${DB_AUTO_INIT:-false}"

>&2 echo "Starting application on port ${PORT:-5000}..."
exec gunicorn \
  --bind "0.0.0.0:${PORT:-5000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 60 \
  --no-control-socket \
  --graceful-timeout 30 \
  --access-logfile - \
  --error-logfile - \
  src.main:app
