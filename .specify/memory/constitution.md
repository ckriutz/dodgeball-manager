<!--
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0 (initial definition with core principles)
- Added sections: Frontend Framework, Backend Framework, Simplicity and Maintainability, Database, Deployment, Additional Constraints, Development Workflow
- Templates requiring updates: None (templates are general and align with principles)
- Follow-up TODOs: None
-->
# Dodgeball Manager Constitution

## Core Principles

### Frontend Framework
The frontend MUST use React with Tailwind CSS. Components should be simple, reusable, and follow React best practices. Tailwind CSS for styling to ensure responsive and maintainable UI without complex CSS frameworks.

### Backend Framework
The backend MUST use Python FastAPI. APIs MUST be RESTful, leverage async capabilities where appropriate, and use Pydantic for data validation and serialization.

### Simplicity and Maintainability
Code MUST be kept simple and avoid over-engineering. Follow YAGNI (You Aren't Gonna Need It) principles. Complexity MUST be justified and added only when necessary through refactoring.

### Database
When databases are needed, PostgreSQL MUST be used. Use appropriate ORMs like SQLAlchemy for database interactions to ensure portability and maintainability.

### Deployment
All services MUST be deployed using Docker containers. Each service MUST have a Dockerfile and .dockerignore for efficient and consistent builds.

## Additional Constraints
Technology Stack: Node.js for React development, Python 3.8+ for FastAPI. Use TypeScript for React components if complexity warrants it.

Security: Implement basic authentication and authorization. Use HTTPS in production. Validate inputs and handle errors gracefully.

Performance: Keep initial load times reasonable. Optimize images and bundles.

## Development Workflow
Code Review: All changes require pull request review.

Testing: Write unit tests for critical logic. Integration tests for API endpoints.

Version Control: Use Git with feature branches.

## Governance
Constitution supersedes all other practices. Amendments require consensus and documentation. All PRs must verify compliance with principles. Use this constitution for guidance on technology choices.

**Version**: 1.0.0 | **Ratified**: 2025-10-24 | **Last Amended**: 2025-10-24
