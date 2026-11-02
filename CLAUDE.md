# CLAUDE.md

Guidance for agents working in this repository.

## Project overview

A full-stack AI governance reference application:

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, JWT/bcrypt.
- **Frontend:** React 18, TypeScript, Vite, Material UI, React Router, Axios.
- **Database:** SQLite for local development/tests; PostgreSQL 15 in Docker.
- **Verification:** pytest (32 tests), Jest (8 tests), Playwright (14 E2E tests), production build/preview smoke, Docker Compose smoke.

The running application is a monolith with containerized services, not a microservice mesh. The original broader modules under `src/model_monitoring/`, `src/security/`, `src/documentation_generator/`, `src/gitops/`, `src/chaos_engineering/`, and `src/management_interface/` are prototypes not wired into the API. Do not describe them as active features.

The latest audit evidence is in `docs/evidence/verification-report.md`.

## Commands

### Backend (from the repository root)

```bash
# One-time setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start local API (SQLite by default, port 8000)
python -m uvicorn src.main:app --reload --port 8000

# Or start via the package entry point
python -m src

# Apply migrations
alembic upgrade head

# Tests
pytest tests/ -q
pytest tests/ --cov=src/api --cov=src/database --cov=src/main.py \
  --cov=src/compliance --cov=src/utils --cov-report=term-missing

# Lint/format for the verified API/core scope
flake8 src/api src/database src/main.py src/scripts src/utils \
  src/compliance/checks.py src/compliance/regulatory_alignment.py
black --check src/api src/database src/main.py src/scripts src/utils \
  src/compliance/checks.py src/compliance/regulatory_alignment.py

# Bootstrap an administrator
ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD='<strong-password>' \
ADMIN_USERNAME=admin python -m src.scripts.seed_admin
```

- Local port **8000** is intentional; macOS AirPlay commonly owns 5000.
- `DB_AUTO_INIT=true` creates/stamps a fresh schema and upgrades versioned databases at startup.
- Docker uses `DB_AUTO_INIT=false` because `src/start.sh` runs migrations first.

### Frontend (from `src/frontend`)

```bash
npm ci
npm run dev          # http://127.0.0.1:5173
npm run typecheck    # tsc -b
npm run lint         # ESLint 9 flat config, zero warnings
npm test             # Jest
npm run test:coverage
npm run build        # tsc -b && vite build
npm run format       # Prettier (does not typecheck)
npm run e2e          # Playwright; starts isolated backend on 5001
```

- `VITE_API_PROXY_TARGET` controls the dev/preview proxy target (default `http://127.0.0.1:8000`).
- `VITE_API_URL` should normally stay empty so requests use the same-origin `/api` proxy.
- Playwright uses the installed Chrome channel locally; `CI=true` switches to bundled Chromium.
- E2E writes screenshots to `docs/evidence/screenshots` and reports to `docs/evidence/test-results`.

### Docker

```bash
cp .env.example .env   # set SECRET_KEY and ADMIN_*; never commit .env
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:5002 (container port 5000; host port 5002)
- PostgreSQL: internal only (not published)
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (`admin`/`admin` development default)

The Compose stack was verified healthy (backend, frontend, db, prometheus, grafana).

## Architecture

### Backend layout

- `src/main.py` — FastAPI app, lifespan init/migrations/seed, CORS, security headers, health/readiness/metrics.
- `src/api/routers/` — `auth`, `users`, `models`, `monitoring`, `compliance`, `dashboard`, `security`, `settings`.
- `src/api/security.py` — JWT, passlib/bcrypt, scopes, current-user/role checks.
- `src/database/__init__.py` — URL resolution (`DATABASE_URL` → `POSTGRES_*` → SQLite), engine/session, `init_db`.
- `src/database/models.py` — users, roles, user_roles, audit_logs, model_versions, monitoring_logs, compliance_records, system_metric_samples, system_settings.
- `src/database/bootstrap.py` — idempotent default roles (`admin`, `compliance-officer`, `security-officer`, `user`), safe under multiple workers.
- `src/database/migrations/` — Alembic revisions; the second migration aligns legacy columns.
- `src/compliance/` — regulatory enum/rule engine + configuration checks used by `/compliance/checks/run`.

### Frontend layout

- `src/frontend/src/pages/` — Landing, Auth, Dashboard, Users, Monitoring, Compliance, Security, Config.
- `src/frontend/src/services/` — shared Axios client and per-domain API clients.
- `src/frontend/src/components/ProtectedRoute.tsx` — session validation and role gates.
- `src/frontend/src/components/Layout/` — responsive shell, header/account menu/logout.
- `src/frontend/e2e/` — Playwright fixtures, helpers, and specs.

### Auth and scopes

Scopes: `user`, `admin`, `models`, `compliance`, `security`.

- Superusers get all scopes.
- Regular users get `user` plus their role permission keys.
- Self-registration never creates a superuser.
- `/auth/refresh-token` must verify the password; do not reintroduce the old bypass.
- There is no role-assignment UI; admin status is edited on the Users page.

### Data / migrations

- SQLite is for local development and tests; PostgreSQL for Docker/production.
- The model-version uniqueness is a **unique index** (`uq_model_version`), not a constraint.
- PostgreSQL URLs use the explicit `postgresql+psycopg2://` driver.
- Fresh local DB: app creates/stamps the head. Existing DB: Alembic upgrade.
- Do not commit `ai_safety_governance.db`, coverage output, Playwright artifacts, compliance reports, or `.env`.

## Conventions

- Keep API routes under `/api/v1` (health/docs/metrics remain at root).
- Use Pydantic schemas for request/response validation; never return `hashed_password`.
- Return generic user-facing errors; log the exception server-side.
- Use `src/utils/time.utcnow()` for naive UTC timestamps to avoid the deprecated `datetime.utcnow`.
- Add regression tests for auth/authorization changes and API workflow changes.
- Frontend: keep API calls in `src/services`, handle loading/error/empty states, and add aria labels to icon-only controls.
- Update `docs/evidence/verification-report.md` and relevant docs when behavior changes.
- Never fabricate screenshots, test results, or verification claims.

## Known limitations (do not silently “fix” by overclaiming)

- Compliance checks are configuration-level GDPR/HIPAA/CCPA checks, not legal certification. EO 14110/OMB M-24-10/NIST are design references only.
- No rate limiting, token denylist/rotation, CSP, or enforced MFA.
- JWTs are stored in `localStorage`.
- Settings flags for MFA/IP whitelist/notifications are not enforced and no notification sender exists.
- Monitoring `network` is relative activity, not link saturation.
- `/metrics` exposes only a liveness gauge.
- Kubernetes manifests are static-reviewed but unverified; placeholders and cluster-specific egress/secrets are required.
- Experimental modules require optional heavy dependencies and are not part of the running app.
