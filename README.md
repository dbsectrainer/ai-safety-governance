# AI Safety & Governance Platform

> Enterprise-grade AI safety and governance platform for responsible AI deployment — aligned to EO 14110 and OMB M-24-10 with multi-cloud Kubernetes support.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/) [![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/) [![Kubernetes](https://img.shields.io/badge/kubernetes-1.21+-326ce5.svg)](https://kubernetes.io/) [![EO 14110](https://img.shields.io/badge/EO%2014110-aligned-green.svg)](https://www.whitehouse.gov/briefing-room/presidential-actions/2023/10/30/executive-order-on-the-safe-secure-and-trustworthy-development-and-use-of-artificial-intelligence/) [![OMB M-24-10](https://img.shields.io/badge/OMB%20M--24--10-aligned-green.svg)](https://www.whitehouse.gov/omb/management/ofcio/) [![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

---

## Overview

1. Provides real-time AI model monitoring including drift detection, performance tracking, and explainability generation to support transparent and auditable AI operations.
2. Enforces regulatory compliance across GDPR, CCPA, HIPAA, EO 14110, and OMB M-24-10 through automated policy checks, audit trails, and structured compliance reporting.
3. Implements bias detection and fairness metrics that continuously evaluate model outputs against configurable thresholds with automated remediation and notification workflows.
4. Delivers a FastAPI-based REST API with JWT authentication, role-based access control, and full OpenAPI documentation for integration into existing enterprise systems.
5. Supports multi-cloud Kubernetes deployment on AWS, Azure, and GCP with Istio service mesh, FluxCD GitOps, Prometheus/Grafana monitoring, and Chaos Mesh resilience testing.
6. Maintains a complete SQL-backed audit database (SQLAlchemy + Alembic migrations) with compliance logs and structured JSON reporting for regulatory audit submissions.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client / API Consumers                   │
│         (REST API clients, Dashboard, CLI Tools)            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Gateway                         │
│        JWT Auth │ RBAC │ OpenAPI Docs │ Rate Limiting       │
└──────┬──────────────────┬──────────────────────┬────────────┘
       │                  │                      │
       ▼                  ▼                      ▼
┌─────────────┐  ┌─────────────────┐  ┌──────────────────────┐
│  AI Model   │  │  Safety Monitor │  │  Governance Engine   │
│  Registry   │  │                 │  │                      │
│  Versioning │  │  Explainability │  │  EO 14110 Controls   │
│  A/B Tests  │  │  Bias Detection │  │  OMB M-24-10 Policy  │
│  Deployment │  │  Drift Alerts   │  │  GDPR / CCPA / HIPAA │
└──────┬──────┘  └────────┬────────┘  └──────────┬───────────┘
       │                  │                      │
       └──────────────────┼──────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                           │
│     SQLAlchemy ORM │ Alembic Migrations │ Audit DB         │
│          PostgreSQL / SQLite (dev)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Multi-Cloud Kubernetes                     │
│                                                             │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌───────────┐  │
│  │   AWS   │   │  Azure  │   │   GCP   │   │ Istio /   │  │
│  │  EKS    │   │  AKS    │   │  GKE    │   │ FluxCD /  │  │
│  │  ECR    │   │  ACR    │   │  GCR    │   │ ChaosMesh │  │
│  └─────────┘   └─────────┘   └─────────┘   └───────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│             Alerting & Observability                        │
│     Prometheus │ Grafana │ CloudWatch │ Compliance Logs     │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Features

### AI Model Monitoring & Explainability

The platform provides continuous visibility into deployed AI model behavior, enabling teams to detect and respond to degraded performance before it affects users or compliance posture.

- Real-time model performance monitoring with configurable alert thresholds
- Drift detection across input distributions and output predictions
- Explainability generation for model decisions to support audit requirements
- A/B testing framework for safe model version rollout
- Full audit trail of model versions, deployments, and prediction logs

### Regulatory Compliance (EO 14110, OMB M-24-10, GDPR, CCPA)

Automated compliance checks run on a configurable schedule and produce structured JSON reports suitable for regulatory audit submissions. The system supports multi-framework enforcement in parallel.

| Framework   | Scope                                     | Auto-Remediation |
| ----------- | ----------------------------------------- | ---------------- |
| EO 14110    | Federal AI safety and trustworthy use     | Yes              |
| OMB M-24-10 | Federal agency AI governance              | Yes              |
| GDPR        | Data consent, breach notification (72h)   | Yes              |
| CCPA        | Consumer rights, data deletion (45 days)  | Yes              |
| HIPAA       | Patient data protection, breach reporting | Yes              |
| NIST AI RMF | AI risk management lifecycle              | Configurable     |

- Compliance configuration in `config/compliance_config.json`
- Audit logs written to `compliance_logs/` as timestamped JSON files
- Email notifications to compliance and security teams on threshold violations

### Bias Detection & Fairness

The platform enforces responsible AI principles throughout the model lifecycle, flagging disparate impact and fairness violations before they reach production.

- Configurable fairness metrics per model and use case
- Automated bias detection runs integrated with the compliance reporting pipeline
- Privacy-preserving data handling controls aligned to GDPR and CCPA requirements
- Ethical AI guidelines enforced as machine-readable policy rules

### Multi-Cloud Deployment (Kubernetes)

Production deployments are managed via GitOps with FluxCD and support all three major cloud providers. The Istio service mesh enables mTLS, observability, and traffic management across services.

- Kubernetes 1.21+ manifests in `kubernetes/` for deployment and service configuration
- Prometheus monitoring configurations per cloud (`devops/monitoring/`)
- Istio service mesh config in `kubernetes/service-mesh/istio-config.yaml`
- Chaos engineering via Chaos Mesh (`kubernetes/chaos/chaos-mesh.yaml`)
- GitOps bootstrap via FluxCD (`kubernetes/flux/gotk-components.yaml`)
- AWS, Azure, and GCP Prometheus scrape configs included

### Security & Compliance

- JWT-based authentication with bcrypt password hashing (python-jose, passlib)
- Role-based access control enforced at the API router level
- Encrypted secrets management via AWS Secrets Manager and KMS
- mTLS between services via Istio service mesh
- NIST AI RMF alignment for AI-specific risk management
- EO 14110 Safe, Secure, and Trustworthy AI controls
- OMB M-24-10 Federal AI governance policy enforcement
- GDPR, CCPA, HIPAA compliance automation

---

## Quick Start

### Prerequisites

- Python 3.8 or later
- Docker 20.10+ and Docker Compose
- Kubernetes 1.21+ (for production deployment)
- kubectl, Helm 3.0+, AWS CLI v2 (for cloud deployment)

### Local Development

```bash
# Clone the repository
git clone https://github.com/dbsectrainer/ai-safety-governance.git
cd ai-safety-governance

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate   # Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp config/aws_config.json config/aws_config.local.json
# Edit aws_config.local.json with your credentials

# Start all services
docker-compose up --build

# API available at:  http://localhost:8000
# API docs at:       http://localhost:8000/docs
```

### Running Tests

```bash
pytest --cov=src tests/
```

### Kubernetes Deployment

```bash
# Apply core manifests
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml

# Configure Prometheus monitoring
kubectl apply -f devops/monitoring/prometheus_config.yaml

# Enable Istio service mesh
kubectl apply -f kubernetes/service-mesh/istio-config.yaml

# Enable chaos engineering (optional)
kubectl apply -f kubernetes/chaos/chaos-mesh.yaml
```

For full cloud deployment instructions including AWS EKS setup, IAM roles, KMS encryption, and FluxCD GitOps bootstrap, refer to `DEPLOYMENT.md`.

---

## Production Ready Status

**Core Platform Implemented and Deployable**

- FastAPI application with JWT authentication and RBAC across all routers
- SQLAlchemy models with Alembic migration history (initial schema committed)
- Regulatory alignment engine supporting GDPR, CCPA, HIPAA with audit trail output
- Compliance JSON reporting written to `compliance_logs/` with timestamped files
- Docker and Docker Compose configuration for local and CI deployment
- Kubernetes manifests for multi-cloud deployment (AWS, Azure, GCP)
- Prometheus monitoring configurations per cloud provider
- Istio service mesh configuration and FluxCD GitOps bootstrap files
- Chaos Mesh resilience testing configuration
- pytest + pytest-cov test harness with coverage reporting
- CI/CD pipeline definition in `devops/CI_CD_pipeline.yaml`

### Verification

```bash
# Install dependencies
pip install -r requirements.txt

# Run test suite with coverage
pytest --cov=src tests/

# Start platform locally
docker-compose up --build

# Check API health
curl http://localhost:8000/docs
```

Expected: API documentation loads at `/docs`; compliance endpoints respond at `/compliance`; auth endpoints respond at `/auth`.

---

## Project Structure

```
ai-safety-governance/
├── src/
│   ├── api/
│   │   ├── routers/
│   │   │   ├── auth.py          # JWT authentication
│   │   │   ├── compliance.py    # Compliance API endpoints
│   │   │   ├── models.py        # AI model management
│   │   │   └── users.py         # User management
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   └── security.py          # Auth helpers, RBAC
│   ├── compliance/
│   │   └── regulatory_alignment.py  # EO 14110, GDPR, CCPA engine
│   ├── database/
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   └── migrations/          # Alembic migration scripts
│   ├── chaos_engineering/
│   │   └── chaos_manager.py     # Chaos Mesh integration
│   └── documentation_generator/ # Auto-doc tooling
├── kubernetes/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── chaos/chaos-mesh.yaml
│   ├── flux/gotk-components.yaml
│   └── service-mesh/istio-config.yaml
├── devops/
│   ├── CI_CD_pipeline.yaml
│   ├── logging/cloudwatch_config.json
│   └── monitoring/              # Prometheus configs per cloud
├── config/
│   ├── aws_config.json
│   ├── compliance_config.json
│   └── documentation_config.json
├── docs/
│   ├── architecture.md
│   ├── multi_cloud_deployment.md
│   ├── security_policy.md
│   └── usage.md
├── compliance_logs/             # Runtime compliance audit output
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── DEPLOYMENT.md
└── README.md
```

---

## BE EASY ENTERPRISES Federal Portfolio

| Showcase Project               | Repository                                                                                                   | Description                                       |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------- |
| **Secure RAG Pipeline**        | [Secure-Generative-AI-Platform-on-AWS](https://github.com/dbsectrainer/Secure-Generative-AI-Platform-on-AWS) | AWS Bedrock + RAG with FedRAMP High alignment     |
| **DevSecOps CI/CD**            | [dod-cybersec-ops-framework](https://github.com/dbsectrainer/dod-cybersec-ops-framework)                     | DoD 8570 / NIST RMF aligned pipeline              |
| **Zero Trust Architecture**    | [AEGIS](https://github.com/dbsectrainer/AEGIS)                                                               | FedRAMP High + NIST 800-207 Zero Trust            |
| **FedRAMP Control Automation** | [nist_800_53_scanner](https://github.com/dbsectrainer/nist_800_53_scanner)                                   | NIST 800-53 Rev 5 compliance scanner              |
| **Federal AI Governance**      | **[ai-safety-governance](https://github.com/dbsectrainer/ai-safety-governance)**                             | **This repo**                                     |
| **CMMC 2.0 Dashboard**         | [integrated-cyber-risk-compliance](https://github.com/dbsectrainer/integrated-cyber-risk-compliance)         | CMMC 2.0 readiness assessment                     |
| **FedRAMP 30-Day Guide**       | [cloud-security-best-practices](https://github.com/dbsectrainer/cloud-security-best-practices)               | Day-by-day FedRAMP implementation roadmap         |
| **Agentic AI Workflow**        | [federal-doc-triage-agent](https://github.com/dbsectrainer/federal-doc-triage-agent)                         | Production-ready LangGraph + Bedrock triage agent |

---

## Author

**Donnivis Baker** — [github.com/dbsectrainer](https://github.com/dbsectrainer)
**BE EASY ENTERPRISES** — Federal IT Modernization & Cybersecurity

For questions, partnerships, or federal engagement inquiries, open an issue or reach out directly.

**Document Version:** 1.0 | **Last Updated:** 2026-06-15 | **Primary Compliance Standard:** EO 14110 / OMB M-24-10
