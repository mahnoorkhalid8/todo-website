# ADR 003: Database Choice - Neon Serverless PostgreSQL

## Status
Accepted

## Date
2026-01-05

## Context
We need to select a database solution for the Todo Web Application that provides reliability, scalability, ACID compliance, and good performance for our task management use case. The application requires a robust data persistence layer that supports complex queries, handles concurrent users, and integrates well with our Python backend stack. The solution should also support modern deployment patterns and provide cost-effective scaling options.

## Decision
We will use Neon Serverless PostgreSQL as our database solution.

Specifically:
- Database: PostgreSQL 15+ (via Neon)
- Hosting: Neon Serverless platform
- Connection Management: Built-in connection pooling
- Migration Tool: Alembic
- ORM Integration: SQLModel with PostgreSQL-specific features

## Rationale
PostgreSQL is a mature, open-source relational database known for its reliability, feature richness, and performance. It provides excellent support for complex queries, data integrity, and concurrent operations which are important for our multi-user application.

Neon Serverless adds significant advantages:
- Automatic scaling up and down based on demand
- Built-in connection pooling to handle concurrent connections efficiently
- Serverless billing model (pay per use) which is cost-effective during development
- Branching capabilities for development and testing workflows
- Point-in-time recovery for data safety
- No infrastructure management overhead

The combination with SQLModel provides excellent developer experience with type safety and validation while maintaining the power of PostgreSQL.

## Alternatives Considered
- SQLite: Not suitable for multi-user applications with concurrent access
- MySQL: Less advanced features compared to PostgreSQL, slightly less developer-friendly
- MongoDB: NoSQL approach doesn't align with our relational data model requirements
- PostgreSQL on traditional hosting: Requires more infrastructure management and manual scaling
- Supabase: More features than needed, potential vendor lock-in concerns
- AWS RDS: More complex setup and management compared to Neon

## Consequences
Positive:
- Automatic serverless scaling based on usage
- Built-in connection pooling and branch management
- Mature SQL database with advanced features
- Cost-effective during development and low usage
- Strong data consistency and ACID compliance
- Excellent integration with SQLModel and Python ecosystem

Negative:
- Vendor lock-in to Neon platform (though still standard PostgreSQL)
- Potential cold start issues during scaling events
- Limited control over database configuration compared to self-hosted
- Learning curve for Neon-specific features

## References
- specs/1-todo-web-app/data-model.md
- specs/1-todo-web-app/plan.md
- backend/models.py
- backend/db.py