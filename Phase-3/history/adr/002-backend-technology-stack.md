# ADR 002: Backend Technology Stack - FastAPI with SQLModel and Neon PostgreSQL

## Status
Accepted

## Date
2026-01-05

## Context
We need to select a backend technology stack for the Todo Web Application that provides high performance, excellent developer experience, strong type safety, and robust API capabilities. The application requires a modern Python web framework that supports asynchronous operations, integrates well with PostgreSQL, and provides built-in support for API documentation and validation.

## Decision
We will use FastAPI with SQLModel and Neon Serverless PostgreSQL as our backend technology stack.

Specifically:
- Web Framework: FastAPI 0.104+
- ORM: SQLModel 0.0.8+
- Database: Neon Serverless PostgreSQL
- API Documentation: OpenAPI 3.0 with automatic generation
- Authentication: JWT-based tokens with middleware support

## Rationale
FastAPI provides excellent performance through asynchronous support and automatic request/response validation using Pydantic models. It generates interactive API documentation automatically, which is crucial for API contract consistency and developer onboarding.

SQLModel is an ORM that combines SQLAlchemy and Pydantic, providing the best of both worlds: robust database operations with type safety and validation. It allows us to define models once and use them for both database operations and API request/response validation.

Neon Serverless PostgreSQL offers serverless scalability, built-in connection pooling, and seamless integration with modern applications. It provides the reliability and features of PostgreSQL with the convenience of serverless infrastructure.

The combination provides:
- High performance through async/await support
- Strong type safety with Pydantic integration
- Automatic API documentation generation
- Robust database operations with SQLModel
- Scalable serverless database infrastructure

## Alternatives Considered
- Django: More complex for API-only applications, heavier framework with more built-in components than needed
- Flask: Requires more manual setup for validation, documentation, and async support
- Starlette: Lower-level than needed, requires more manual implementation of common features
- Tortoise ORM: Async-first but less mature than SQLModel/SQLAlchemy
- Traditional SQLAlchemy: More verbose than SQLModel, separate validation layer needed

## Consequences
Positive:
- High-performance async API endpoints
- Automatic request/response validation and serialization
- Interactive API documentation generation
- Type safety across the stack
- Seamless model sharing between database and API layers
- Serverless database scaling

Negative:
- Learning curve for developers unfamiliar with FastAPI dependency injection
- SQLModel is relatively new compared to traditional ORMs
- Potential complexity in advanced database operations
- Dependency on async programming patterns

## References
- specs/1-todo-web-app/plan.md
- specs/1-todo-web-app/data-model.md
- specs/1-todo-web-app/contracts/openapi.yaml