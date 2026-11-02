# Frontend — AI Safety Governance Platform

React 18 + TypeScript + Vite + Material UI client for the FastAPI backend.

## Commands

```bash
npm ci
npm run dev          # http://127.0.0.1:5173 (proxies /api to 127.0.0.1:8000)
npm run typecheck    # tsc -b
npm run lint         # ESLint, zero warnings
npm test             # Jest
npm run test:coverage
npm run build        # tsc -b && vite build
npm run e2e          # Playwright (starts isolated backend on 5001)
```

Environment:

- `VITE_API_URL` — leave empty to use the same-origin `/api` proxy.
- `VITE_API_PROXY_TARGET` — dev/preview proxy target, default `http://127.0.0.1:8000`.
- Docker Compose sets the target to `http://backend:5000`.

## Structure

- `src/pages/` — Landing, Auth, Dashboard, Users, Monitoring, Compliance, Security, Configuration.
- `src/services/` — shared Axios client and API domain modules.
- `src/components/ProtectedRoute.tsx` — session/role gates.
- `e2e/` — Playwright specs, fixtures, and helpers.
- `scripts/smoke-production.mjs` — production-preview smoke test.

See the root [`README.md`](../../README.md) and [`docs/evidence/verification-report.md`](../../docs/evidence/verification-report.md) for the full verified feature set and limitations.
