# Audit Evidence Index

All artifacts in this directory were produced during the verification audit on 2026-11-01 and come from the actual running application, tests, builds, or Docker stack. No screenshot is a mockup.

## Reports

- [`verification-report.md`](verification-report.md) — full audit, fixes, commands, results, screenshots, limitations, and final verdict.

## Screenshots (`screenshots/`)

| File | Source | Demonstrates |
| --- | --- | --- |
| `homepage-desktop.png` | Vite dev server | Public landing page, desktop |
| `homepage-mobile.png` | Vite dev server | Public landing page, 390×844, no horizontal overflow |
| `login-desktop.png` | Vite dev server | Login form |
| `register-desktop.png` | Vite dev server | Registration form |
| `dashboard-desktop.png` | Vite dev server | Live dashboard with seeded model/compliance data |
| `dashboard-new-user.png` | Vite dev server | New user dashboard |
| `dashboard-regular-user.png` | Vite dev server | Regular-user dashboard |
| `dashboard-mobile.png` | Vite dev server | Mobile dashboard |
| `users-admin.png` | Vite dev server | Admin user CRUD table |
| `users-mobile.png` | Vite dev server | Mobile user management |
| `compliance-checks.png` | Vite dev server | Configured compliance checks, score, audit activity |
| `monitoring-desktop.png` | Vite dev server | Host resource and model monitoring |
| `security-desktop.png` | Vite dev server | Security posture checks/events/recommendations |
| `configuration-settings.png` | Vite dev server | Persisted non-secret settings |
| `unauthorized.png` | Vite dev server | Regular user denied admin page |
| `homepage-production.png` | `vite preview` + `dist/` | Production bundle landing page |
| `dashboard-production.png` | `vite preview` + `dist/` | Production bundle after real login |
| `homepage-docker.png` | Docker Compose frontend | Containerized landing page |
| `dashboard-docker.png` | Docker Compose frontend | Containerized dashboard with PostgreSQL |

## Test results (`test-results/`)

| File | Contents |
| --- | --- |
| `backend-coverage.txt` | 32 pytest tests and 80% API/core coverage |
| `frontend-coverage.txt` | 8 Jest tests and component coverage |
| `e2e-run.txt` | Full Playwright run log (14 passed) |
| `playwright-results.json` | Machine-readable Playwright results |
| `playwright-report/` | Playwright HTML report |
| `compliance-report.json` | Report exported from the compliance UI during E2E |
| `api-smoke.txt` | Local Gunicorn endpoint/login/role/refresh smoke test |
| `npm-audit.txt` | Production dependency audit (0 vulnerabilities) |
| `npm-audit-all.txt` | Full dev-toolchain audit (remaining advisories) |
| `pip-audit.txt` | Python dependency audit |

## Build/runtime results (`build-results/`)

| File | Contents |
| --- | --- |
| `frontend-build.log` | `tsc -b && vite build` output |
| `production-smoke.txt` | Production preview login/console/API smoke test |
| `docker-compose-config.txt` | Validated Compose configuration |
| `docker-compose-ps.txt` | Final container status |
| `docker-images.txt` | Built image inventory |
| `docker-backend.log`, `docker-frontend.log` | Container logs |
| `docker-runtime-verification.txt` | Health, proxied login, migrations, roles, Prometheus, Grafana |
| `docker-smoke.txt` | Dockerized frontend login/console/API smoke test |

## Reproduce

See the README sections “Testing and validation”, “Docker Compose”, and “Production build”, or run:

```bash
.venv/bin/pytest tests/ --cov=src/api --cov=src/database --cov=src/main.py \
  --cov=src/compliance --cov=src/utils --cov-report=term-missing
cd src/frontend
npm run lint && npm run typecheck && npm test && npm run build && npm run e2e
```
