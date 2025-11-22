# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Safety & Governance platform that provides comprehensive tools for responsible AI development, monitoring, and compliance. **Updated for 2025 industry standards**, the platform implements a microservices architecture with FastAPI backend, React/TypeScript frontend, and includes advanced monitoring, security, and compliance features.

### 2025 Standards Compliance
- **EU AI Act** (August 2025 GPAI requirements)
- **NIST AI Risk Management Framework** (RMF 1.0 + 2025 updates)
- **OWASP LLM Top 10** security controls
- **ISO 42001** AI Management Systems alignment

## Development Commands

### Backend (Python/FastAPI)
- **Start development environment**: `docker-compose up --build`
- **Run backend only**: `cd src && python main.py`
- **Database migrations**: `alembic upgrade head`
- **Run tests**: `pytest`
- **Lint**: `flake8 src/`
- **Format**: `black src/`
- **Type checking**: `mypy src/`

### Frontend (React/TypeScript)
- **Development server**: `cd src/frontend && npm run dev`
- **Build**: `cd src/frontend && npm run build`
- **Test**: `cd src/frontend && npm test`
- **Test with coverage**: `cd src/frontend && npm run test:coverage`
- **Lint**: `cd src/frontend && npm run lint`
- **Lint fix**: `cd src/frontend && npm run lint:fix`
- **Format**: `cd src/frontend && npm run format`

### Docker & Deployment
- **Full development stack**: `docker-compose up --build`
- **Kubernetes deployment**: `kubectl apply -f kubernetes/`
- **Production build**: Build using Dockerfile in project root

## Architecture Overview

### Core Services
- **Backend API** (FastAPI): REST API with authentication, compliance, and model management
- **Frontend** (React/TypeScript): Web interface with Material-UI components
- **Database** (PostgreSQL): Primary data storage with Alembic migrations
- **Monitoring** (Prometheus/Grafana): Metrics collection and visualization

### Key Modules (2025 Update)
- **Model Monitoring** (`src/model_monitoring/`):
  - A/B testing, fairness monitoring, drift detection
  - **NEW:** AI Bill of Materials (AIBOM) tracking (`ai_bom.py`)
  - **NEW:** Model registry with versioning (`model_registry.py`)
  - **NEW:** Model cards and data sheets for transparency

- **Security** (`src/security/`):
  - **NEW:** AI red teaming and adversarial testing (`ai_red_teaming.py`)
  - Threat detection, privacy protection, differential privacy
  - **NEW:** OWASP LLM Top 10 security controls
  - **NEW:** Prompt injection and jailbreak detection

- **Compliance** (`src/compliance/`):
  - **NEW:** EU AI Act compliance framework (`eu_ai_act.py`)
  - **NEW:** NIST AI Risk Management Framework (`nist_ai_rmf.py`)
  - Regulatory alignment and compliance frameworks
  - **NEW:** Automated compliance reporting

- **Documentation Generator** (`src/documentation_generator/`): Automated documentation generation
- **GitOps** (`src/gitops/`): Infrastructure deployment management
- **Chaos Engineering** (`src/chaos_engineering/`): Resilience testing

### Database
- Uses SQLAlchemy ORM with Alembic for migrations
- Database models in `src/database/models.py`
- Connection configuration supports PostgreSQL

### API Structure
- All API routes prefixed with `/api/v1/`
- Authentication endpoints: `/api/v1/auth/`
- User management: `/api/v1/users/`
- Compliance: `/api/v1/compliance/`
- Model management: `/api/v1/models/`
- Health check: `/health`

### Frontend Architecture
- Vite build system with TypeScript
- Material-UI for components
- React Router for navigation
- Axios for API communication
- Jest for testing with Testing Library
- Protected routes with authentication

## Configuration Files

### Backend Configuration
- `requirements.txt`: Python dependencies
- `alembic.ini`: Database migration configuration
- `config/`: JSON configuration files for AWS, compliance, and documentation
- Environment variables loaded from `config/secrets.env`

### Frontend Configuration
- `src/frontend/package.json`: Node.js dependencies and scripts
- `src/frontend/vite.config.ts`: Vite build configuration
- `src/frontend/tsconfig.json`: TypeScript configuration
- ESLint and Prettier configurations for code quality

### Docker Configuration
- `Dockerfile`: Multi-stage build for production
- `docker-compose.yml`: Development environment with all services
- `src/frontend/Dockerfile.dev`: Frontend development container

## Development Workflow

### Local Development
1. Ensure Docker and Docker Compose are installed
2. Run `docker-compose up --build` to start all services
3. Backend available at `http://localhost:5002`
4. Frontend available at `http://localhost:5173`
5. Grafana dashboard at `http://localhost:3000` (admin/admin)
6. Prometheus at `http://localhost:9090`

### Database Setup
- PostgreSQL runs in Docker container
- Migrations handled by Alembic
- Database initialization occurs automatically via `src/start.sh`

### Testing
- Backend: Use `pytest` for Python tests
- Frontend: Use `npm test` for React component tests
- Coverage reports available for frontend with `npm run test:coverage`

### Code Quality
- Backend: Black formatting, Flake8 linting, MyPy type checking
- Frontend: ESLint, Prettier, TypeScript strict mode
- Pre-commit hooks configured via Husky and lint-staged

## Key Implementation Details

### Security Features
- JWT-based authentication
- CORS configuration for cross-origin requests
- Differential privacy implementation
- Threat detection and prevention
- Secret management system

### Monitoring & Observability
- Prometheus metrics collection
- Grafana visualization
- Model performance monitoring
- Fairness and bias detection
- Predictive monitoring with rollback capabilities

### Compliance Framework (2025 Update)
- **EU AI Act Compliance**
  - Risk classification (Unacceptable, High, Limited, Minimal)
  - GPAI model requirements and transparency reports
  - Prohibited practices monitoring
- **NIST AI RMF 2025**
  - GOVERN, MAP, MEASURE, MANAGE functions
  - Generative AI Profile (NIST AI 600-1)
  - Privacy Framework 1.1 integration
- **Traditional Compliance**
  - GDPR and CCPA compliance tools
  - Regulatory alignment tracking
  - Audit trail generation
  - Privacy-preserving techniques

### Infrastructure
- Kubernetes deployment configurations
- GitOps with FluxCD integration
- Service mesh (Istio) configuration
- Chaos engineering capabilities
- Multi-cloud deployment support

## Important Notes

- The platform focuses on defensive security and responsible AI practices
- **2025 Compliance**: EU AI Act, NIST AI RMF, and OWASP LLM Top 10
- All model monitoring includes fairness and bias detection with intersectional analysis
- Privacy protection is built into core functionality (GDPR, CCPA, EU AI Act)
- Infrastructure is designed for high availability and disaster recovery
- Compliance frameworks are integrated throughout the system
- **NEW:** AI red teaming and adversarial testing for security validation
- **NEW:** Model registry and AIBOM for supply chain transparency
- **NEW:** Automated transparency reporting for regulatory compliance

## New 2025 Features

### AI Red Teaming (`src/security/ai_red_teaming.py`)
- Automated adversarial testing against OWASP LLM Top 10
- Prompt injection, jailbreak, and data poisoning detection
- Privacy leakage and model extraction prevention
- Comprehensive vulnerability scanning and reporting

### AI Bill of Materials (`src/model_monitoring/ai_bom.py`)
- Complete component inventory (models, datasets, frameworks, libraries)
- Dependency tracking and vulnerability scanning
- License compliance analysis
- CycloneDX and SPDX export formats

### Model Registry (`src/model_monitoring/model_registry.py`)
- Version control and approval workflows
- Model cards with comprehensive documentation
- Data sheets for datasets
- Lifecycle management (development → testing → production)

### EU AI Act Compliance (`src/compliance/eu_ai_act.py`)
- Risk classification system
- GPAI model compliance (August 2025 requirements)
- Technical documentation and transparency reporting
- Prohibited practices monitoring

### NIST AI RMF (`src/compliance/nist_ai_rmf.py`)
- Four core functions: GOVERN, MAP, MEASURE, MANAGE
- Generative AI Profile implementation
- Risk assessment and tracking
- Comprehensive compliance reporting