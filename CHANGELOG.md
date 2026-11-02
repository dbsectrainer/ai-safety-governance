# Changelog

All notable changes to the AI Safety & Governance project will be documented in this file.

## [2.2.0] - 2026-11-01

### Fixed

- Local startup no longer requires PostgreSQL; `DATABASE_URL`, `POSTGRES_*`, and SQLite fallback are supported.
- Alembic schema drift (`name`, `version_metadata`, `version_id`, `users.full_name`, new settings/sample tables) corrected for SQLite and PostgreSQL.
- Authentication bypass in `/auth/refresh-token` fixed; password is re-verified.
- Superusers now receive all required API scopes; `/users/me` and login return roles; protected routes no longer crash on missing roles.
- Registration validates username/password and ignores client-supplied privilege fields.
- Docker Compose no longer references a missing secrets env file or a nonexistent start script; PostgreSQL driver explicitly uses psycopg2; multi-worker admin/role seeding races handled.
- Monitoring, dashboard, security, settings, and compliance-check APIs added and wired to the UI (replacing mock data).
- Frontend TypeScript, ESLint, Jest Watchman, layout overflow, logout, and dead-link defects fixed.
- Landing page no longer hides the hero/features behind entrance animations before they complete; a first-paint E2E regression test guards it.
- Fresh SQLite databases no longer race schema initialization when multiple Gunicorn workers start.
- Production dependency audit reduced to zero vulnerabilities after non-breaking updates.
- Prometheus target corrected; Docker stack verified healthy.
- Kubernetes manifests statically corrected for the actual port/probes and removed obsolete APIs.

### Added

- 27 API/integration tests and 14 Playwright end-to-end tests.
- Real user-management, compliance-run/export, monitoring, security-posture, and persisted-settings workflows.
- `.github/workflows/ci.yml`, `.env.example`, MIT `LICENSE`, production preview smoke script, and audit evidence/report.
- Default RBAC roles and administrator bootstrap CLI.

### Changed

- Local backend port standardized to 8000 (macOS AirPlay conflicts on 5000); Docker backend remains 5000 internally and 5002 on the host.
- README, usage, architecture, deployment, and CLAUDE guidance now reflect only verified functionality and documented limitations.

### Known limitations

- Compliance automation is configuration-level GDPR/HIPAA/CCPA only; EO 14110/OMB M-24-10/NIST are design references.
- Kubernetes deployment is unverified; experimental ML/security modules are not wired.
- No rate limiting, token revocation, CSP, or enforced MFA; JWTs are stored in localStorage.

## [2.1.0] - 2024-02-15

### Added

- Enhanced Documentation Generation
  - Automated code analysis for documentation
  - Markdown generation from source code
  - Comprehensive architecture documentation
  - Inline code documentation extraction

- Expanded Compliance Framework
  - Multi-jurisdictional regulatory alignment
  - Enhanced reporting mechanisms
  - Automated compliance log generation
  - Dynamic regulatory requirement tracking

- Advanced Security Enhancements
  - Extended threat detection capabilities
  - Improved secret management
  - Advanced privacy guard mechanisms
  - Comprehensive security configuration management

- Predictive Model Monitoring
  - Enhanced explainability features
  - Advanced root cause analysis
  - Improved anomaly detection algorithms
  - Extended time series forecasting

- Chaos Engineering Improvements
  - More granular infrastructure chaos testing
  - Enhanced resilience simulation
  - Multi-cloud chaos testing support
  - Improved chaos scenario management

### Changed

- Refined GitOps deployment strategies
- Improved configuration management
- Enhanced multi-cloud support
- Optimized performance monitoring
- Streamlined user management interface

### Fixed

- Resolved minor bugs in monitoring systems
- Improved error handling across modules
- Enhanced logging and traceability
- Fixed configuration synchronization issues
- Improved dependency management

## [2.0.0] - 2024-01-20

### Added

- Model Fairness Monitoring
  - Demographic parity and equal opportunity metrics
  - Individual and group fairness assessment
  - Feature importance tracking
  - Automated bias detection

- A/B Testing Framework
  - Statistical testing with multiple methods
  - Experiment tracking and management
  - Automated conclusion based on significance
  - Comprehensive metrics collection

- Automated Model Rollback
  - Multiple rollback triggers
  - Version management and tracking
  - Integration with AWS SageMaker
  - Automated rollback execution

- GitOps Workflow
  - FluxCD configuration
  - Automated infrastructure synchronization
  - Multi-environment support
  - Notification system

- Service Mesh Implementation
  - Istio configuration
  - Traffic management
  - Enhanced security policies
  - Advanced observability
  - mTLS encryption

- Chaos Engineering
  - Comprehensive chaos testing
  - Network chaos simulation
  - Resource stress testing
  - Scheduled resilience testing
  - AWS infrastructure chaos testing

- Differential Privacy
  - Multiple privacy mechanisms
  - Privacy budget management
  - Composition theorem implementation
  - Sensitivity estimation

- Enhanced Security
  - Automated secret rotation
  - Zero-trust security model
  - Advanced threat detection
  - Comprehensive security scanning

- Predictive Monitoring
  - Time series analysis
  - Root cause analysis
  - Correlation analysis
  - Anomaly detection

### Changed

- Updated deployment process with GitOps workflow
- Enhanced security architecture with service mesh
- Improved monitoring system with predictive capabilities
- Upgraded CI/CD pipeline with security scanning
- Enhanced privacy protection mechanisms
- Updated documentation for all new features

### Fixed

- Improved error handling in monitoring system
- Enhanced security policy enforcement
- Fixed compliance checking mechanisms
- Improved metric collection reliability
- Enhanced system resilience

## [1.0.0] - 2023-12-15

### Initial Release

- Basic model monitoring
- Simple security measures
- Initial AWS integration
- Basic documentation
- Core functionality implementation

### Features

- Model performance monitoring
- Basic security controls
- AWS deployment support
- Docker containerization
- Kubernetes orchestration

## [0.1.0] - 2023-11-01

### Alpha Release

- Project structure setup
- Initial documentation
- Basic AWS configuration
- Development environment setup
- Testing framework implementation

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the tags on this repository.

## Version Categories

- Major version changes (X.0.0) indicate significant architectural changes or major feature additions
- Minor version changes (0.X.0) indicate new features and functionality additions
- Patch version changes (0.0.X) indicate bug fixes and minor improvements

## Update Process

1. Version numbers are updated based on the scope of changes
2. Changelog entries are added for each release
3. Documentation is updated to reflect changes
4. Release notes are generated for each version
5. Tags are created in the repository

## Maintenance

- Regular updates for security patches
- Periodic review of dependencies
- Continuous improvement of features
- Regular testing and validation
- Documentation updates
