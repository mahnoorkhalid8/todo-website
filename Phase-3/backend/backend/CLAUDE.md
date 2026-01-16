# Backend Guidelines

## Stack
- FastAPI
- SQLModel (ORM)
- Neon PostgreSQL
- JWT Authentication
- Alembic (Migrations)

## Project Structure
- `main.py` - FastAPI app entry point
- `models.py` - SQLModel database models
- `routes/` - API route handlers
  - `auth.py` - Authentication endpoints
  - `tasks.py` - Task management endpoints
- `schemas/` - Pydantic models for request/response validation
  - `auth.py` - Authentication schemas
  - `tasks.py` - Task schemas
- `services/` - Business logic services
  - `auth_service.py` - Authentication business logic
  - `task_service.py` - Task business logic
- `utils/` - Utility functions
  - `auth.py` - Authentication utilities
  - `validation.py` - Validation utilities
- `dependencies/` - FastAPI dependencies
  - `auth.py` - Authentication dependencies
  - `database.py` - Database dependencies
- `db.py` - Database connection and session management
- `config.py` - Configuration settings

## API Conventions
- All routes under `/api/` prefix
- Return JSON responses
- Use Pydantic models for request/response
- Handle errors with HTTPException
- All authenticated routes require JWT token in Authorization header

## Database
- Use SQLModel for all database operations
- Connection string from environment variable: DATABASE_URL
- Models defined in models.py with proper relationships
- Use services layer for business logic instead of direct model access

## Running
- Development: `uvicorn main:app --reload --port 8000`
- With environment: `DATABASE_URL=postgresql://... uvicorn main:app --reload --port 8000`

## Testing
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Contract tests in `tests/contract/`