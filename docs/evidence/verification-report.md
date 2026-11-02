# Verification Report — AI Safety & Governance Platform

**Audit date:** 2026-11-01 (America/New_York; Docker/UTC evidence dated 2026-11-02)
**Repository:** `ai-safety-governance`
**Scope:** full repository audit, dependency/configuration review, defect remediation, application execution, automated testing, browser E2E verification, production build, Docker deployment, evidence capture, and documentation.

---

## 1. Executive summary

The repository contained a substantial FastAPI backend and a React/TypeScript frontend, but the application could not be used end-to-end. The most serious problems were a database configuration that only worked inside a specific Docker network, an ORM/migration schema mismatch, a token-refresh endpoint that issued tokens without verifying the password, an RBAC scope gap that made admin/compliance/model APIs unreachable even for administrators, and a frontend whose primary pages displayed mock data rather than calling the API.

All application-breaking defects found in the verified scope were fixed. The backend now starts locally with SQLite and in Docker with PostgreSQL; authentication, authorization, user management, model monitoring, compliance checks, dashboard aggregation, security posture, settings persistence, responsive navigation, and logout were exercised against the running stack. The production bundle was served from `vite preview` and exercised with a real login. The Docker Compose stack (backend, frontend, PostgreSQL, Prometheus, Grafana) was built and verified healthy.

**Final verdict: PASS** for the locally runnable, production-build, and Docker Compose paths. Kubernetes was not applied to a cluster and is explicitly unverified; experimental ML/security modules and known dependency advisories remain documented limitations.

| Verification | Result |
| --- | --- |
| Backend pytest | **32 passed**, 2 upstream warnings, 80% API/core coverage |
| Frontend Jest | **8 passed**, 72.34% line coverage for the two covered components |
| ESLint / TypeScript | **pass** / **pass** |
| Production build | **pass** (`tsc -b && vite build`) |
| Playwright E2E | **14 passed**, no console errors, no API failures |
| Production preview smoke | **pass**, login + dashboard rendered from `dist/` |
| Docker Compose | **5/5 services healthy**, migrations + login + Prometheus + Grafana verified (backend UID 1000) |
| API smoke | **all checked endpoints 200**, refresh bypass returns 401 |
| Production npm audit | **0 vulnerabilities** |
| Full dev npm audit | 66 advisories (2 low, 60 moderate, 4 high) remain in dev/transitive tooling; production audit is 0 |
| Python dependency audit | 3 advisories in `python-jose`/`ecdsa` (documented) |
| Kubernetes | **not verified** — no cluster available |

---

## 2. Method

1. Inventoried every tracked source file, configuration, migration, test, Docker/Kubernetes manifest, CI definition, and documentation page.
2. Ran the existing checks before changing code: `pytest`, `tsc -b`, `npm run build`, `npm run lint`, `npm test`, and backend startup/auth requests.
3. Reproduced failures and traced them to root causes (database URL, schema mismatch, scope grants, missing routes/services, build script behavior, proxy/port conflicts).
4. Implemented minimal fixes within the existing architecture, adding regression tests for auth/authorization and API workflows.
5. Ran the application locally (SQLite), through a production bundle (`vite preview`), and through Docker Compose (PostgreSQL + Prometheus + Grafana).
6. Used Playwright to exercise real user journeys at desktop and mobile viewports, collecting screenshots and asserting no browser console errors or failed API requests.
7. Updated the README, usage/architecture/deployment notes, CI workflow, environment example, and this report with reproducible commands and evidence.

### Environment

| Item | Observed |
| --- | --- |
| OS | macOS (darwin), 2026-11-01 |
| Python | 3.12.7 (virtualenv `.venv`) |
| Node / npm | 26.13.0 / 11.20.0 |
| Browser | Google Chrome via `@playwright/test` 1.55.0 |
| Docker | Docker 29.9.2, Compose v5.6.1 |
| Local DB | SQLite 3.50.6 at `ai_safety_governance.db` (untracked) |
| Container DB | PostgreSQL 15 |
| Local API | Gunicorn + Uvicorn worker on `127.0.0.1:8000` |
| Production preview | Vite preview on `127.0.0.1:4173` |
| Docker URLs | frontend `:5173`, backend `:5002`, Prometheus `:9090`, Grafana `:3000` |

---

## 3. Initial findings and baseline

### Baseline command results

| Command | Initial result |
| --- | --- |
| `pytest tests/` | 5 passed — only the compliance unit tests existed; no API tests |
| `npx tsc -b` | **23 TypeScript errors** (axios types, unused symbols, unknown Axios responses) |
| `npm run build` | falsely "succeeded" because the script ran `tsc` against a solution config with no files |
| `npm run lint` | failed: `--ext` is not valid with ESLint 9 flat config |
| `npm test` | crashed: Watchman `fchmod` permission error in the sandbox |
| `GET /health` | 200 |
| `POST /api/v1/auth/token` | **500** — engine tried `db:5432` on every request |
| Docker build | not run initially; daemon unavailable |
| Frontend pages | Dashboard/Users/Compliance/Security/Configuration used mock data; monitoring called endpoints that did not exist |

### Defects found and resolved

| ID | Severity | Defect / root cause | Fix and files | Verification |
| --- | --- | --- | --- | --- |
| DB-1 | Critical | `get_database_url()` always built a PostgreSQL URL with host `db`, so local runs failed every DB request. | `src/database/__init__.py` now supports `DATABASE_URL`, `POSTGRES_*`, and a SQLite default; SQLite thread arguments handled. | Local Gunicorn login/dashboard 200; API smoke. |
| DB-2 | Critical | Alembic migration created `model_name`/`model_metadata`/`model_version_id`, while ORM models used `name`/`version_metadata`/`version_id`; the committed SQLite DB was stamped but stale. | New migration `20261101_120000_align_schema.py`; initial migration formatted; `env.py` uses shared URL resolution and batch mode for SQLite; startup creates/stamps fresh DBs and upgrades versioned DBs. | SQLite and PostgreSQL schemas inspected; `/ready` 200; Docker migration at revision `7a1c9f2d4b6e`. |
| AUTH-1 | Critical | `POST /auth/refresh-token` issued a token for any known username without checking the password (authentication bypass). | `src/api/routers/auth.py` now verifies password and active state, supports email/username, and returns a fresh token with user profile. | Regression test `test_refresh_token_requires_the_correct_password`; API smoke returns 401 for wrong password. |
| AUTH-2 | Critical | Superusers received only `user` + `admin` scopes; compliance/model/security APIs required scopes that no normal or admin account could hold. Admin UI routes also depended on a missing `roles` field and crashed. | `scopes_for_user()` grants all scopes to superusers plus role permission keys; `/users/me` and login return roles; `ProtectedRoute` handles roles safely; admin checks use `is_superuser`/roles. | API test matrix (403 for regular user, 200 for admin); E2E admin pages and regular-user denial. |
| AUTH-3 | High | Self-registration accepted an `is_superuser` field and the old UI asked for an unused `name`; no safe admin bootstrap. | Registration ignores privilege fields, stores `full_name`, validates username/password; admin seed CLI + `ADMIN_*` startup bootstrap; `seed_admin`/roles retry on multi-worker races. | Tests for duplicate/weak/invalid registration and privilege escalation; Docker two-worker startup without unique-constraint traceback. |
| API-1 | High | No monitoring endpoints existed; the monitoring page called `/api/monitoring/*`. | New `monitoring.py`: host metrics via `psutil`, persisted samples, model metrics/performance, alerts. | E2E monitoring page; API tests; screenshots. |
| API-2 | High | Dashboard, Users, Compliance, Security, and Configuration pages used hard-coded/mock data or local-only state. | Added dashboard/security/settings services and real API-backed pages; user CRUD and compliance checks call the backend; settings persist in `system_settings`. | E2E CRUD, compliance run/export, settings reload persistence; screenshots. |
| API-3 | High | Compliance failure path crashed (`report_path` was a `str`, code used `.name`); compliance checks were not callable from the API. | Added `/compliance/checks/run`, `/summary`; fixed report path handling; JSON-safe audit details. | Backend tests and API smoke score=100. |
| API-4 | Medium | Compliance/audit/security errors returned raw `str(e)` and some pages had no error states. | Generic user-facing errors with server-side `logger.exception`; added error/empty/loading states to frontend pages. | Code review, API tests, E2E console/API assertions. |
| FE-1 | High | TypeScript failed; build script did not typecheck; lint command invalid; Jest crashed on Watchman. | `package.json` scripts now use `tsc -b`, valid ESLint invocation, `test:ci`; removed `@types/axios`; fixed axios generics/error typing; Jest `watchman: false`. | `tsc -b`, ESLint, Jest 8/8, build all pass. |
| FE-2 | High | Vite proxy target was Docker-only (`backend:5000`), and local port 5000 is commonly occupied by macOS AirPlay. | Proxy default is `http://127.0.0.1:8000`, configurable through `VITE_API_PROXY_TARGET`; preview also proxies. | Local and production-preview login smoke. |
| FE-3 | High | Layout applied both the permanent drawer width and a margin, causing ~8–68px horizontal overflow; status chip overflowed metric cards. | Removed duplicate offset; responsive temporary drawer for mobile; metric-card flex wrapping. | E2E `expectNoHorizontalOverflow`; mobile screenshots. |
| FE-4 | Medium | Logout/profile menu items did nothing; "Forgot password" dead link; Unauthorized "Go to Dashboard" went to `/`. | Implemented logout with client token cleanup; removed dead link; fixed navigation; responsive header/sidebar. | E2E logout and regular-user flows. |
| FE-5 | Medium | Header and Sidebar fetched `/users/me` on unauthenticated protected routes, producing 401 console errors. | Auth cache/shared request; skip user fetch without a token. | E2E unauthenticated redirect has no console/API failures. |
| FE-6 | High | Landing hero/feature content was wrapped in `Fade`/`Slide` entrance transitions. Before/while they ran, the only visible text was the non-animated "Key Features" heading — reproduced in the earlier production screenshot and reported by the user as "the homepage only says Key Features". | Removed content-hiding entrance transitions from `pages/Landing/index.tsx`; content renders at full opacity immediately. Added a first-paint E2E assertion. | E2E #14 checks h1/feature opacity is 1 immediately after render; production and Docker homepage screenshots recaptured. |
| OPS-1 | High | Docker Compose referenced a missing `config/secrets.env`, mounted `./start.sh` (nonexistent), used an EOL Python 3.8 image, and hid migration failures with `|| true`. | Compose env/healthchecks/ports fixed; Dockerfile Python 3.12 + non-root UID 1000; `start.sh` waits for DB, runs migrations strictly, uses `--no-control-socket`; DB no longer published. | Docker build and 5-service health verification. |
| OPS-2 | High | SQLAlchemy 2.1 resolved `postgresql://` to psycopg3, but only psycopg2 was installed. | URL explicitly uses `postgresql+psycopg2://`. | Docker stack healthy and migrated. |
| OPS-3 | High | `recreate="always"` batch migration failed on PostgreSQL because the monitoring-log foreign key depends on the model-version primary key. | Removed forced recreation; unique index now created separately; PostgreSQL migration re-run from an empty volume. | Docker migration at head; schema inspected. |
| OPS-4 | Medium | Prometheus scraped `app:5000` although the Compose service is `backend`. | Target updated to `backend:5000`. | Prometheus target health `up`. |
| SEC-1 | Medium | Security headers were absent; CORS origin was hard-coded; default secret was silently accepted. | Security-header middleware, env-driven CORS, secret-strength check in security posture, explicit non-wildcard CORS. | curl headers; tests; security page screenshot. |
| SEC-2 | High | 25 production npm advisories (including axios critical advisories) and no CI workflow. | `npm audit fix` (non-breaking) upgraded axios/react-router and transitive packages; production audit is now 0. Added `.github/workflows/ci.yml`. | `npm audit --omit=dev` 0; lint/typecheck/tests/build/E2E re-run. |
| OPS-5 | Medium | Generated DB, coverage HTML, and stale compliance report were tracked; UI/CI docs claimed checks that did not exist. | Removed generated artifacts from the index, added `.gitignore` entries; rewrote README and docs; added CI workflow. | `git ls-files` contains no generated DB/coverage/playwright artifacts. |
| OPS-6 | High | Starting Gunicorn with two workers against a fresh SQLite DB raced schema creation/stamping; one worker exited (`Worker failed to boot`). | Added a cross-process initialization lock (SQLite file lock / PostgreSQL advisory lock) around create/stamp/upgrade in `src/database/__init__.py`. | Fresh DB + 2 Gunicorn workers: health 200, login 200, both workers survived; production smoke passed. |
| K8S-1 | High (unverified) | Deployment used container port 8080 while the app listens on 5000; probes/ingress referenced a separate 9090 metrics port; init container chmod could not work on a read-only ConfigMap; a removed PodSecurityPolicy API was present. | Ports/probes/ServiceMonitor/service aligned to 5000; logs emptyDir added; init container and PSP removed; invalid ingress `auth_request` block removed; duplicate NetworkPolicy key merged. | YAML parses; static review only — **not applied to a cluster**. |

---

## 4. Features and workflows tested

### Automated backend tests (`tests/`)

32 tests across `test_auth.py`, `test_users.py`, `test_platform.py`, and the compliance unit test. They cover:

- health/readiness/root/metrics and security headers;
- registration, duplicate/weak/invalid input, privilege-escalation prevention;
- login, wrong password, inactive account, refresh-token verification (the security regression);
- token/session requirements and 403 boundaries for regular users;
- admin user CRUD, password reset, activation/deactivation, self-protection, deletion;
- model version lifecycle, duplicate rejection, monitoring logs, performance snapshots;
- compliance check run, summary, record CRUD, audit logs, JSON report;
- monitoring system/resources/performance/endpoints and unknown resource handling;
- dashboard aggregates, settings defaults/update/persistence/validation;
- security posture checks and default RBAC role seeding;
- CORS allow/deny behavior.

### Frontend tests

Jest + Testing Library covers the two monitoring components (loading, data, empty history, color thresholds, tooltips/accessibility labels).

### Browser E2E (`src/frontend/e2e`, Playwright)

14 tests, one worker, Chrome:

| # | Journey | Assertions |
| --- | --- | --- |
| 1 | Administrator dashboard | Seeded model + compliance data, live cards, growth chart, activity, screenshot |
| 2 | User administration | Create → edit name → deactivate → delete through the API-backed UI |
| 3 | Compliance | Run checks, 100% score, three regulations, audit activity, JSON download parsed |
| 4 | Monitoring | Host stats, resource chart, model performance, healthy status |
| 5 | Security | Control checks, RBAC/secret/CORS/admin/token/audit checks, events, recommendations |
| 6 | Configuration | Change retention/debug, save, reload, values persisted |
| 7 | Registration + login | Register a new user, login, dashboard, screenshot |
| 8 | Logout | Token cleared and login page shown |
| 9 | Regular-user boundaries | `/users` blocked with Unauthorized page; dashboard still usable |
| 10 | Landing responsiveness | Desktop and 390×844 mobile; no horizontal overflow |
| 11 | Login navigation | Landing CTA reaches login |
| 12 | Unauthenticated access | `/dashboard` redirects to login without 401 noise |
| 13 | Mobile navigation | Drawer opens, routes to Users, no horizontal overflow |
| 14 | Landing first paint | Hero heading and feature card have opacity 1 immediately after render; guards against content-hiding entrance animations |

Every E2E test automatically fails on browser console errors, uncaught page errors, failed `/api` requests, or any `/api` response ≥ 400.

---

## 5. Validation commands and results

### Backend

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m pytest tests/ \
  --cov=src/api --cov=src/database --cov=src/main.py \
  --cov=src/compliance --cov=src/utils --cov-report=term-missing
.venv/bin/python -m flake8 src/api src/database src/main.py src/scripts \
  src/utils src/compliance/checks.py src/compliance/regulatory_alignment.py
.venv/bin/python -m black --check src/api src/database src/main.py src/scripts \
  src/utils src/compliance/checks.py src/compliance/regulatory_alignment.py
```

Result: `32 passed, 2 warnings`; **80% total coverage** for the selected API/core scope; Flake8 and Black pass. Evidence: [`backend-coverage.txt`](test-results/backend-coverage.txt).

The two warnings are upstream: Starlette's httpx deprecation notice and passlib's Python `crypt` deprecation.

### Frontend

```bash
cd src/frontend
npm run lint          # pass, zero warnings
npm run typecheck     # pass
npm test -- --runInBand
npm run test:coverage -- --runInBand
npm run build
```

Result: 8/8 Jest tests pass; 72.34% lines / 74% statements for the two covered components; production build succeeds. Evidence: [`frontend-coverage.txt`](test-results/frontend-coverage.txt), [`frontend-build.log`](build-results/frontend-build.log).

### End-to-end

```bash
cd src/frontend
npm run e2e
```

Result: **14 passed (49.0s)**, 0 skipped, 0 flaky. Evidence: [`e2e-run.txt`](test-results/e2e-run.txt), [`playwright-results.json`](test-results/playwright-results.json), HTML report at [`playwright-report/index.html`](test-results/playwright-report/index.html). Screenshots in [`screenshots`](screenshots).

### API smoke (local Gunicorn)

```bash
.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker --no-control-socket src.main:app
```

Result: `/health`, `/ready`, `/docs`, `/openapi.json` (28 paths), admin login, users, dashboard, monitoring, compliance run (score 100), security summary, settings all 200; wrong-password refresh returns 401. Evidence: [`api-smoke.txt`](test-results/api-smoke.txt).

### Production build and preview

```bash
cd src/frontend
npm run build
npm run preview -- --host 127.0.0.1 --port 4173
node scripts/smoke-production.mjs
```

Result: built HTML + hashed assets served; landing rendered; admin login through `/api` proxy reached `/dashboard`; `consoleErrors: []`, `apiFailures: []`. Evidence: [`production-smoke.txt`](build-results/production-smoke.txt); screenshots `homepage-production.png`, `dashboard-production.png`.

### Docker Compose

```bash
cp .env.example .env   # set SECRET_KEY and ADMIN_*
docker compose up --build -d
```

Result: backend, frontend, PostgreSQL, Prometheus, and Grafana all healthy. Verified:

- backend `/health` 200, `/ready` database connected;
- frontend proxied login 200 with admin roles;
- Alembic revision `7a1c9f2d4b6e`; columns `name`, `version_metadata`, `version_id`;
- 1 admin, 4 seeded roles;
- Prometheus targets `ai-safety-governance` and `prometheus` both `up`;
- Grafana health `database: ok`;
- Docker screenshots `homepage-docker.png`, `dashboard-docker.png` with no console/API errors.

Evidence: [`docker-runtime-verification.txt`](build-results/docker-runtime-verification.txt), [`docker-compose-ps.txt`](build-results/docker-compose-ps.txt), [`docker-backend.log`](build-results/docker-backend.log), [`docker-compose-config.txt`](build-results/docker-compose-config.txt).

### Security and dependency checks

| Check | Result | Evidence |
| --- | --- | --- |
| `npm audit --omit=dev` | 0 vulnerabilities | [`npm-audit.txt`](test-results/npm-audit.txt) |
| `npm audit` (all/dev) | 66 advisories remain in dev toolchain/transitives (2 low, 60 moderate, 4 high); production audit is 0 | [`npm-audit-all.txt`](test-results/npm-audit-all.txt) |
| `pip-audit -r requirements.txt` | 3 advisories: python-jose 3.5.0 (1), ecdsa 0.19.2 (2) | [`pip-audit.txt`](test-results/pip-audit.txt) |
| Refresh-token bypass regression | 401 for wrong password; test passes | `tests/api/test_auth.py` |
| CORS | allowed origin gets header; disallowed origin does not | `test_cors_allows_configured_origin_only` |
| Security headers | present on responses | API test and curl evidence |

---

## 6. Screenshot evidence

All images are genuine captures from the running application, not mockups.

| Screenshot | Demonstrates |
| --- | --- |
| [`homepage-desktop.png`](screenshots/homepage-desktop.png) | Public landing page, desktop |
| [`homepage-mobile.png`](screenshots/homepage-mobile.png) | Public landing page, 390×844, no horizontal overflow |
| [`login-desktop.png`](screenshots/login-desktop.png) | Login form and validation structure |
| [`register-desktop.png`](screenshots/register-desktop.png) | Registration form |
| [`dashboard-desktop.png`](screenshots/dashboard-desktop.png) | Live aggregate dashboard with seeded model/compliance data |
| [`dashboard-new-user.png`](screenshots/dashboard-new-user.png) | Newly registered user's dashboard |
| [`dashboard-regular-user.png`](screenshots/dashboard-regular-user.png) | Regular-user dashboard (admin-only navigation hidden) |
| [`dashboard-mobile.png`](screenshots/dashboard-mobile.png) | Responsive dashboard, 390×844 |
| [`users-admin.png`](screenshots/users-admin.png) | Admin user table with create/edit/deactivate/delete actions |
| [`users-mobile.png`](screenshots/users-mobile.png) | Mobile user management after drawer navigation |
| [`compliance-checks.png`](screenshots/compliance-checks.png) | 100% configuration-check score, GDPR/HIPAA/CCPA cards, audit activity |
| [`monitoring-desktop.png`](screenshots/monitoring-desktop.png) | Real host utilization, persisted history, model performance |
| [`security-desktop.png`](screenshots/security-desktop.png) | Six control checks, events, recommendations |
| [`configuration-settings.png`](screenshots/configuration-settings.png) | Persisted settings after reload |
| [`unauthorized.png`](screenshots/unauthorized.png) | Regular user blocked from `/users` |
| [`homepage-production.png`](screenshots/homepage-production.png) | Production `dist/` bundle served by `vite preview` |
| [`dashboard-production.png`](screenshots/dashboard-production.png) | Production bundle after real login through preview proxy |
| [`homepage-docker.png`](screenshots/homepage-docker.png) | Landing page served by the Dockerized frontend |
| [`dashboard-docker.png`](screenshots/dashboard-docker.png) | Dashboard served by Docker Compose with PostgreSQL |

The compliance JSON download is preserved at [`test-results/compliance-report.json`](test-results/compliance-report.json).

---

## 7. Changes summary

### Backend

- Added `monitoring`, `dashboard`, `security`, and `settings` routers.
- Added `SystemMetricSample`, `SystemSetting`, user `full_name`, RBAC `role_names`/`permission_scopes`, and unique model-version index.
- Reworked database URL resolution, startup migration/stamp behavior, and Alembic env.
- Added schema-alignment migration; fixed PostgreSQL batch-migration behavior.
- Fixed refresh-token authentication bypass; added scope grants for superusers and safe role handling.
- Added user CRUD, password reset, self-protection, audit entries, and validation.
- Added compliance check runner/summary and safe JSON report handling; configurable audit/config paths.
- Added security headers, CORS env configuration, readiness probe, liveness metrics, and health metadata.
- Added idempotent default role seeding and admin bootstrap with multi-worker race handling.
- Added `python-dotenv`, `psutil`, bcrypt pin, and explicit psycopg2 driver.

### Frontend

- Replaced mock Dashboard/Users/Compliance/Security/Configuration data with real API services.
- Added shared Axios client, error extraction, auth cache, logout, and token cleanup.
- Added responsive layout/drawer, metric-card wrapping, loading/error/empty states, and accessible labels.
- Added user CRUD UI, compliance run/export, settings persistence, live monitoring, security posture.
- Fixed TypeScript errors, ESLint configuration/scripts, Jest Watchman failure, Vite proxy/port behavior, and production preview proxy.
- Updated HTML title/favicon/meta and removed dead links.
- Added Playwright configuration, fixtures, 14 E2E tests, and production smoke script.
- Removed homepage entrance animations that could hide the hero/features, and added a first-paint regression test.
- Added a cross-process DB initialization lock so multi-worker starts against a fresh SQLite DB do not race.

### Operations/docs

- Dockerfile: Python 3.12, UID 1000, curl health check, `.dockerignore`.
- Compose: health checks, DB internal-only, env configuration, correct backend driver, frontend proxy target.
- Prometheus local target fixed; Docker stack verified.
- Kubernetes manifests statically corrected (ports, probes, PSP removal, volumes, network policy, ingress).
- Added GitHub Actions CI, `.env.example`, LICENSE, README rewrite, usage/architecture/CLAUDE docs rewrite, and this report.
- Removed generated database/coverage/compliance artifacts from version control; added ignores.

---

## 8. Remaining issues and limitations

| Item | Severity | Status / rationale |
| --- | --- | --- |
| Kubernetes deployment unverified | High (deployment) | No cluster available. Manifests parse and obvious port/API errors were fixed; placeholders and DB egress still require operator input. |
| `python-jose` / `ecdsa` advisories | Medium | Reported by `pip-audit`; no fix version in the pinned line. The app uses HS256, not ECDSA. Replacing the JWT library is a follow-up. |
| Dev dependency advisories | Low–Medium | 66 advisories in Jest/Playwright/ESLint transitive packages (2 low, 60 moderate, 4 high); production dependencies audit clean. Non-breaking `npm audit fix` was applied; the remainder lacks a non-breaking resolution. |
| No rate limiting / token revoke / MFA enforcement | Medium | Documented. Frontend client-side attempts were removed; no backend lockout or denylist. |
| JWT in `localStorage`, no CSP | Medium | Documented XSS risk. A CSP and httpOnly-cookie design would require an architectural change. |
| Experimental modules | Medium | `model_monitoring`, `security`, `documentation_generator`, `gitops`, `chaos_engineering`, `management_interface` need optional dependencies and are not wired. |
| Legal/regulatory coverage | High (scope) | Automated checks are configuration-level GDPR/HIPAA/CCPA; EO 14110/OMB M-24-10/NIST are design references, not certified controls. |
| Role assignment UI | Low | Default roles exist; assigning roles requires DB/API work. Superuser management is available. |
| Settings not enforced | Low | MFA/IP whitelist/notification flags persist but no enforcement/sender exists. |
| SQLite production use | Medium | SQLite is for local/tests; use PostgreSQL for multi-worker production. |
| CI not executed on GitHub | Low | Workflow committed; equivalent local commands all pass. |
| Docker secrets defaults | Medium | Compose uses development placeholders for `SECRET_KEY`, PostgreSQL, and Grafana; operators must override them. |
| `npm run e2e` local browser | Low | Uses installed Chrome channel locally; CI uses bundled Chromium. |
| K8s Prometheus rules | Low | `devops/monitoring/prometheus_config.yaml` is a reference configuration with K8s assumptions; not deployed. |
| Model/fairness/drift automation | Medium | Monitoring logs are API-supplied; no inference pipeline or automatic fairness/drift evaluation is running. |

---

## 9. Reproducibility checklist

- [x] Dependencies install from lockfiles (`npm ci`, pinned Python requirements).
- [x] Application starts locally with SQLite and documented commands.
- [x] PostgreSQL/Docker startup works and migrations reach head.
- [x] Production frontend build completes and serves.
- [x] TypeScript, ESLint, Flake8, and Black pass for the verified scope.
- [x] Backend and frontend automated tests pass.
- [x] Browser E2E passes with no console errors or failed API calls.
- [x] Desktop and mobile screenshots captured from the running app.
- [x] Docker Compose stack verified healthy end-to-end.
- [x] README and this report reflect the verified state.
- [x] Generated secrets/data are not tracked.
- [x] Remaining issues are documented, not hidden.

**Final status: PASS for the verified local, production-build, and Docker Compose scope. Kubernetes and the experimental modules are explicitly out of verified scope.**
