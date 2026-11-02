#!/usr/bin/env bash
# Start an isolated backend instance for Playwright end-to-end tests.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-$ROOT/.venv/bin/python}"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="$(command -v python3)"
fi

E2E_DIR="$ROOT/.e2e"
rm -rf "$E2E_DIR"
mkdir -p "$E2E_DIR/compliance_logs"

export DATABASE_URL="sqlite:///$E2E_DIR/ai-safety-e2e.db"
export SECRET_KEY="e2e-only-secret-key-not-for-production"
export CORS_ORIGINS="http://127.0.0.1:5173,http://localhost:5173"
export ADMIN_EMAIL="e2e-admin@example.com"
export ADMIN_PASSWORD="E2eAdmin123!"
export ADMIN_USERNAME="admin"
export ADMIN_FULL_NAME="E2E Administrator"
export COMPLIANCE_AUDIT_DIR="$E2E_DIR/compliance_logs"
export PYTHONUNBUFFERED=1

"$PYTHON_BIN" -m alembic upgrade head
export DB_AUTO_INIT=false

exec "$PYTHON_BIN" -m uvicorn src.main:app \
  --host 127.0.0.1 \
  --port "${E2E_PORT:-5001}" \
  --log-level info
