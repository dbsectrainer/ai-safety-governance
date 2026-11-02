# Copilot Instructions for AI Safety & Governance Platform

This guide enables AI coding agents to be immediately productive in this codebase. It summarizes architecture, workflows, conventions, and integration points unique to this project.

## Architecture Overview

- **Monorepo Structure**: Contains backend (Python), frontend (React/TypeScript), DevOps, docs, and configuration.
- **Backend** (`src/`):
  - **API**: FastAPI-based, with routers for `auth`, `compliance`, `models`, `users`.
  - **Compliance**: Regulatory alignment logic in `src/compliance/`.
  - **Database**: SQLAlchemy models and Alembic migrations in `src/database/`.
  - **Chaos Engineering**: Tools for resilience testing in `src/chaos_engineering/`.
  - **Model Monitoring**: Fairness, explainability, rollback in `src/model_monitoring/`.
  - **Security**: Privacy, threat detection, secret management in `src/security/`.
- **Frontend** (`src/frontend/`):
  - React + Vite + TypeScript. See `src/frontend/README.md` for ESLint and build details.
- **DevOps** (`devops/`, `kubernetes/`, `docker-compose.yml`):
  - Multi-cloud deployment (AWS, Azure, GCP, local) via Prometheus configs and Kubernetes manifests.
  - CI/CD pipeline in `devops/CI_CD_pipeline.yaml`.

## Developer Workflows

- **Backend**:
  - Run: `python src/main.py` or use `src/start.sh`.
  - Migrations: Alembic scripts in `src/database/migrations/`.
  - Tests: Run with `pytest tests/`.
- **Frontend**:
  - Install: `npm install` in `src/frontend/`.
  - Dev server: `npm run dev`.
  - Tests: `npm run test` (Jest).
  - Lint: `npm run lint` (ESLint config in `eslint.config.js`).
- **Deployment**:
  - Docker: Use `Dockerfile` and `docker-compose.yml` for local or cloud builds.
  - Kubernetes: Manifests in `kubernetes/` for cluster deployment.

## Project-Specific Conventions

- **API Routing**: All endpoints are defined in `src/api/routers/`. Use FastAPI's router pattern.
- **Compliance Logic**: Regulatory checks are modularized in `src/compliance/regulatory_alignment.py`.
- **Monitoring**: Prometheus configs for each cloud in `devops/monitoring/`.
- **Documentation**: Markdown-based, generated via `src/documentation_generator/`.
- **Secrets**: Managed in `src/security/secret_manager.py`.
- **Logs**: Compliance logs in `compliance_logs/`.

## Integration Points

- **Cloud Providers**: Configs in `config/` and `devops/monitoring/` for AWS, Azure, GCP.
- **Database**: SQLite by default (`ai_safety_governance.db`), can be swapped via config.
- **CI/CD**: Pipeline defined in `devops/CI_CD_pipeline.yaml`.
- **Security**: Advanced privacy and threat detection modules in `src/security/`.

## Examples

- To add a new API endpoint, create a router in `src/api/routers/` and register it in `src/main.py`.
- To extend compliance checks, add logic to `src/compliance/regulatory_alignment.py` and corresponding tests in `tests/compliance/`.
- For frontend changes, update React components in `src/frontend/src/` and run `npm run dev` to preview.

## References

- [docs/architecture.md](docs/architecture.md): System architecture details
- [docs/usage.md](docs/usage.md): Usage instructions
- [src/frontend/README.md](src/frontend/README.md): Frontend build/lint/test setup

---

For unclear or missing sections, ask the user for clarification or examples from their workflow.
