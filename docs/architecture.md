# Architecture

This document describes the architecture that is actually implemented and verified. Some original design modules remain in the repository as prototypes; they are listed at the end and are not part of the running API.

## System context

```
Browser
  │
  │ React 18 SPA (Vite, MUI, React Router)
  │  static assets + /api/* requests
  ▼
Reverse proxy / Vite proxy
  │
  ▼
FastAPI application (src/main.py)
  ├── JWT authentication + scope enforcement
  ├── /api/v1/users, /models, /compliance, /monitoring,
  │   /dashboard, /security, /settings
  ├── SQLAlchemy 2.x ORM ──► SQLite (local/tests) or PostgreSQL (Docker)
  ├── psutil host sampling ──► system_metric_samples
  └── compliance runner ──► compliance_records + compliance_logs/*.json
```

Prometheus scrapes `/metrics` (liveness gauge); Grafana is available in Docker Compose. The application does not currently expose full request/model metrics.

## Backend

### Entry point and lifecycle

`src/main.py` creates the FastAPI app and a lifespan context that:

1. resolves the database URL (`DATABASE_URL`, `POSTGRES_*`, or local SQLite);
2. creates and stamps a fresh schema, or applies pending Alembic migrations for a versioned database (`DB_AUTO_INIT`);
3. seeds the four default RBAC roles idempotently;
4. optionally bootstraps an administrator from `ADMIN_EMAIL`/`ADMIN_PASSWORD`.

The app adds CORS middleware driven by `CORS_ORIGINS` and baseline security headers.

### Routers

| Router | Responsibility | Authorization |
| --- | --- | --- |
| `auth.py` | login, registration, password-verified refresh, logout | public |
| `users.py` | `/me`, admin user CRUD, activation, password reset | `user` / `admin` |
| `models.py` | model version registry and monitoring-log ingestion | `models` |
| `monitoring.py` | system metrics, persisted samples, model performance, alerts | `user` (read-only) |
| `compliance.py` | compliance records, check execution, summary, audit logs | `compliance` |
| `dashboard.py` | aggregate counts, health, growth, activity | `user` |
| `security.py` | observable security posture and recommendations | `security` |
| `settings.py` | persisted non-secret settings | `admin` |

### Authentication and authorization

- OAuth2 password flow (`/api/v1/auth/token`) accepts email or username.
- Passwords are bcrypt hashes via `passlib`.
- JWT claims include `sub`, `scopes`, `exp`, and `iat`; HS256 by default.
- Superusers receive `user`, `admin`, `models`, `compliance`, and `security`.
- Regular users receive `user` plus permission keys from assigned roles.
- `get_current_user` enforces required scopes; `RoleChecker` is available for role-name checks.
- `/auth/refresh-token` re-verifies the supplied password (regression tested).
- There is no server-side token denylist or refresh-token rotation.

### Data model

| Table | Purpose |
| --- | --- |
| `users` | Accounts, full name, bcrypt hash, active/superuser flags |
| `roles` / `user_roles` | RBAC roles and assignments |
| `model_versions` | Model name/version/metadata/status; unique `(name, version)` index |
| `monitoring_logs` | Version-scoped metric name/value/timestamp |
| `compliance_records` | Regulation/status/details/next review |
| `audit_logs` | Actor, action, resource, details, timestamp |
| `system_metric_samples` | Host resource samples for monitoring charts |
| `system_settings` | Single-row JSON settings document |

### Migrations

- `be9906a7d2c3` — original initial schema (legacy column names).
- `7a1c9f2d4b6e` — aligns columns with the ORM, adds `users.full_name`, the model-version unique index, monitoring indexes, `system_metric_samples`, and `system_settings`.
- SQLite uses Alembic batch mode; PostgreSQL uses transactional DDL.
- Fresh local databases can be created directly from ORM metadata and stamped at head; Docker always runs `alembic upgrade head` before starting Gunicorn.

### Background/operational behavior

- Host resource samples are persisted when `/monitoring/system` or `/monitoring/resources/*` is called; samples older than 24 hours are pruned.
- Compliance report files are written to `compliance_logs/` (configurable).
- No background worker, queue, or scheduled notification sender is implemented.

## Frontend

- React 18 + TypeScript + Vite.
- MUI theme and components; React Router for routes; Axios client with token injection.
- Route-level lazy loading via `React.lazy`.
- `ProtectedRoute` validates the session with `/users/me` and enforces admin/role gates.
- Shared auth cache avoids duplicate `/users/me` calls from Header/Sidebar.
- All API calls use relative `/api/v1` in development; Vite proxies to the backend. `VITE_API_URL` supports a separately hosted API.
- Loading, empty, success, and error states are implemented on the data pages.
- Responsive behavior: permanent sidebar on desktop, temporary drawer on mobile; metric cards wrap and tables scroll internally.

### Routes

| Route | Access |
| --- | --- |
| `/` | public |
| `/login`, `/register`, `/unauthorized` | public |
| `/dashboard` | authenticated |
| `/monitoring` | authenticated |
| `/users`, `/config` | admin |
| `/compliance` | admin/compliance-officer |
| `/security` | admin/security-officer |

## Deployment topologies

### Local development

- SQLite file at the repository root (untracked).
- Backend via `uvicorn` on 8000.
- Vite dev server on 5173 with `/api` proxy.
- No external services required.

### Docker Compose (verified)

- Frontend Vite container on 5173, proxying to `backend:5000`.
- Backend container: Python 3.12, non-root UID 1000, Gunicorn + Uvicorn worker, port 5000 published as 5002.
- PostgreSQL 15 reachable only on the Compose network.
- Prometheus scrapes `backend:5000/metrics`; Grafana runs on 3000.
- `start.sh` waits for the database, applies migrations, then starts Gunicorn.

### Kubernetes (reference, unverified)

Manifests in `kubernetes/` were statically reviewed and corrected for the application port (5000), `/ready` probe, logging volume, removed PodSecurityPolicy, service/ServiceMonitor port naming, duplicate NetworkPolicy keys, and ingress metrics exposure. They still require:

- substitution of `${ECR_REGISTRY}`, `${IMAGE_TAG}`, `${AWS_ACCOUNT_ID}`;
- secrets/config maps (`ai-safety-secrets`, `ai-safety-config`, `ai-safety-certs`);
- database connectivity and egress rules for the target cluster;
- a cluster to apply and validate them.

No Kubernetes deployment was performed in this audit.

## Original/experimental modules

These modules are retained but are not imported by `src/main.py` and are not verified:

| Module | Original purpose | Current state |
| --- | --- | --- |
| `src/model_monitoring/` | drift, fairness, A/B testing, explainability, predictive rollback | prototypes; require NumPy/pandas/scikit-learn/statsmodels/SHAP/LIME |
| `src/security/` | threat detection, differential privacy, secret manager | prototypes; require boto3/ML dependencies; not wired |
| `src/compliance/regulatory_alignment.py` | rule engine used by the API | active |
| `src/documentation_generator/` | automated docs | prototype; optional networkx/markdown2/pygments |
| `src/gitops/` | deployment management | prototype |
| `src/chaos_engineering/` | Chaos Mesh integration | prototype |
| `src/management_interface/` | dashboard/user/configuration helpers | prototype |

The README and verification report list the resulting limitations explicitly.
