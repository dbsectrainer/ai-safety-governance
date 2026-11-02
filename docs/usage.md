# Usage Guide

This guide describes the functionality that is actually implemented and verified in this repository. For installation and verification evidence, see the [README](../README.md) and the [verification report](evidence/verification-report.md).

## Access URLs

| Environment | Frontend | API | Docs |
| --- | --- | --- | --- |
| Local development | <http://127.0.0.1:5173> | <http://127.0.0.1:8000> | <http://127.0.0.1:8000/docs> |
| Docker Compose | <http://localhost:5173> | <http://localhost:5002> | <http://localhost:5002/docs> |
| Production preview | <http://127.0.0.1:4173> | proxied through `/api` to 8000 | — |

Local development uses port 8000 to avoid the macOS AirPlay Receiver on port 5000. The Docker backend listens on port 5000 inside the container and is published as 5002.

## Accounts and roles

- Self-registration creates an active, non-superuser account.
- An administrator can be created with the `ADMIN_*` environment variables or the CLI:

```bash
ADMIN_EMAIL=admin@example.com \
ADMIN_PASSWORD='<a-strong-password>' \
ADMIN_USERNAME=admin \
python -m src.scripts.seed_admin
```

- Passwords require at least 8 characters, uppercase, lowercase, a number, and a special character.
- The four seeded RBAC roles are `admin`, `compliance-officer`, `security-officer`, and `user`.
- Superusers receive all API scopes. Regular users receive the `user` scope plus any role permission keys.
- There is currently no role-assignment screen; superuser status can be changed by an administrator on the Users page.

## Pages

### Landing (`/`)

Public overview of the platform with calls to register or sign in. Responsive at mobile and desktop widths.

### Login / Register (`/login`, `/register`)

- Email + password login against the FastAPI OAuth2 password flow.
- Registration creates a non-superuser account.
- Successful login redirects to the dashboard (or the originally requested protected page).
- Sign out is available from the account menu in the header and removes the stored token.

### Dashboard (`/dashboard`)

Shows aggregate data from the database:

- active users and active model versions;
- latest compliance score;
- host CPU/memory/disk-based health label;
- cumulative users/models over the last 24 hours;
- recent audit activity (all users for administrators; own activity for regular users).

### Users (`/users`, admin only)

Administrators can:

- list users;
- create a user with a role (User/Admin) and active status;
- edit username, email, full name, role, active status, or reset the password;
- deactivate/reactivate users;
- delete users (with confirmation).

The backend prevents deleting/demoting the currently signed-in administrator.

### Monitoring (`/monitoring`)

- Current CPU, memory, disk, and relative network activity from the host.
- Persisted resource samples charted over time (a new sample is recorded by the monitoring endpoints).
- Active model count, accuracy, average latency, and error rate derived from model monitoring logs.
- Per-model performance chart for registered model versions.
- Alerts derived from non-compliant/needs-review compliance records and unhealthy models.

`network` is relative host network activity, not a measurement of link saturation.

### Compliance (`/compliance`, admin/compliance scope)

- “Run Checks” executes the configuration checks in `src/compliance/checks.py`.
- Results are stored as compliance records and written to `compliance_logs/` as timestamped JSON reports.
- The summary shows the latest record per regulation and an overall score.
- “Export Report” downloads the currently displayed records as JSON.
- Recent audit activity includes compliance and administrative audit entries.

**Important:** these are configuration-level checks against values in `config/compliance_config.json`. They do not collect evidence, certify compliance, or constitute legal advice. EO 14110, OMB M-24-10, and NIST AI RMF are design references only.

### Security (`/security`, admin/security scope)

Displays observable controls and recent audit events:

- RBAC roles configured;
- non-placeholder JWT secret strength;
- restricted CORS origins;
- at least one active administrator;
- access-token lifetime ≤ 60 minutes;
- audit-log table availability.

The report can be downloaded as JSON. This page reports observable application configuration; it does not perform a full vulnerability assessment.

### Configuration (`/config`, admin only)

Persists non-secret settings in the database:

- general: platform name, environment, debug flag, data retention, max concurrent models;
- security: password policy label, session timeout, IP whitelist, MFA flag, audit logging;
- integrations: AWS region, monitoring service;
- notifications: email/Slack digest flags and alert threshold.

Webhooks, API tokens, and credentials are intentionally **not** accepted or stored here. The MFA, IP-whitelist, and notification flags are configuration values only; they are not enforced or sent.

## Model registry and monitoring API

There is no model-creation page. Use the API:

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin@example.com&password=<password>' \
  | python -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

# Register a model version
curl -X POST http://127.0.0.1:8000/api/v1/models/versions \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name":"risk-classifier","version":"1.0.0","version_metadata":{"framework":"sklearn"},"status":"deployed"}'

# Record a metric (use the returned version id)
curl -X POST http://127.0.0.1:8000/api/v1/models/monitoring \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"version_id":1,"metric_name":"accuracy","metric_value":{"value":0.94}}'
```

Registered versions and metrics appear on the Monitoring page. This is a log/registry, not an inference service.

## Compliance workflow

```bash
curl -X POST http://127.0.0.1:8000/api/v1/compliance/checks/run \
  -H "Authorization: Bearer $TOKEN"

curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/v1/compliance/summary
```

Outputs:

- records in the `compliance_records` table;
- audit entries in `audit_logs`;
- JSON reports and audit logs under `compliance_logs/` (or `COMPLIANCE_AUDIT_DIR`).

The checked thresholds are:

| Framework | Configuration requirement |
| --- | --- |
| GDPR | breach notification ≤ 72 hours and notification contacts present |
| HIPAA | breach reporting ≤ 60 days and 100% access-logging coverage declared |
| CCPA | data-deletion response ≤ 45 days and opt-out mechanism declared |

Edit `config/compliance_config.json` to match your own controls; re-run checks afterwards.

## Monitoring and observability

- `GET /health` — process liveness (no database access).
- `GET /ready` — database connectivity (503 when unavailable).
- `GET /metrics` — a liveness gauge in Prometheus exposition format.
- Prometheus/Grafana in Docker Compose verify scraping and dashboard availability; the app does not currently export request, latency, or model metrics beyond the liveness gauge.
- Docker Compose: Prometheus <http://localhost:9090>, Grafana <http://localhost:3000> (`admin`/`admin` for local development only).

## Troubleshooting

| Symptom | Cause / resolution |
| --- | --- |
| Frontend loads but API calls fail | Backend not running, wrong port, or `VITE_API_PROXY_TARGET` points elsewhere. Local default is `http://127.0.0.1:8000`. |
| Login works but admin pages show Access Denied | The account is not a superuser and lacks the required role. Use the seeded administrator or promote the user as an admin. |
| `port is already allocated` in Docker | Another local service owns 5173/5002/9090/3000. Stop it or remap the Compose ports. |
| macOS: API on port 5000 behaves strangely | AirPlay Receiver may own 5000. Use 8000 locally or 5002 through Docker. |
| `alembic upgrade head` fails on an old DB | The new schema-alignment migration expects the original initial revision. Back up data and follow the migration error; the provided Docker flow starts from a fresh PostgreSQL volume. |
| Settings changes do not enforce MFA/IP rules | Only persistence is implemented; enforcement is a documented limitation. |
| Compliance checks show 100% but you need regulatory evidence | The checks validate configuration only. Collect and review supporting evidence separately. |

## Resetting local development data

SQLite data is untracked and safe to recreate:

```bash
# Stop the backend first.
rm -f ai_safety_governance.db
python -m uvicorn src.main:app --reload --port 8000
```

For Docker, remove the PostgreSQL volume explicitly (this deletes Docker-local data):

```bash
docker compose down -v
docker compose up --build
```
