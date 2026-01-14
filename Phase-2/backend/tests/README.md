# Todo App Backend - Integration Tests

This directory contains comprehensive integration tests for the Todo application backend, ensuring all components work together correctly with authentication, user isolation, and security measures in place.

## Test Structure

- `test_api_endpoints.py` - Tests all API endpoints with authentication and user isolation
- `test_auth.py` - Authentication flow and JWT token verification tests
- `test_middleware.py` - Authentication middleware and user isolation enforcement
- `test_error_handling.py` - Error handling and edge case tests
- `test_integration.py` - Complete integration workflows
- `test_final_integration.py` - Final comprehensive integration tests

## Running Tests

To run all tests:
```bash
cd backend
pytest tests/ -v
```

To run specific test files:
```bash
pytest tests/test_api_endpoints.py -v
```

To run with coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

## Test Coverage

### Authentication & Security
- JWT token verification and validation
- User isolation enforcement (users can only access their own tasks)
- Authentication middleware functionality
- Token expiration and refresh handling
- Invalid token handling
- Malformed authorization header handling

### API Endpoints
- `GET /api/{user_id}/tasks` - Get all tasks for a user (with filtering)
- `POST /api/{user_id}/tasks` - Create a new task
- `GET /api/{user_id}/tasks/{id}` - Get specific task
- `PUT /api/{user_id}/tasks/{id}` - Update a task
- `DELETE /api/{user_id}/tasks/{id}` - Delete a task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion

### CRUD Operations
- Complete task lifecycle (Create, Read, Update, Delete)
- Task validation (title length, required fields)
- Special character handling
- Large payload handling
- Edge case validation

### Error Handling
- 401 Unauthorized responses
- 403 Forbidden responses (user isolation)
- 404 Not Found responses
- 422 Validation errors
- Server error handling (500)
- Network error handling

### Security Validation
- SQL injection prevention
- XSS prevention
- User ID verification between token and URL
- Task ownership enforcement
- Token replay attack prevention
- Session hijacking prevention

## Testing Approach

Our tests follow these principles:

1. **Authentication Required**: Every endpoint that should require authentication is tested without and with valid/invalid tokens
2. **User Isolation**: Every endpoint is tested to ensure users can only access their own data
3. **Input Validation**: All endpoints are tested with valid, invalid, and edge-case inputs
4. **Error Handling**: All possible error scenarios are tested with appropriate responses
5. **Security Validation**: Potential security vulnerabilities are tested and validated

## Environment Variables for Testing

The tests use the same environment variables as the main application:
- `BETTER_AUTH_SECRET` - Secret for JWT token signing/verification
- `DATABASE_URL` - Database connection string (uses in-memory SQLite for tests)

## Test Fixtures

The test suite uses several fixtures:
- `client` - FastAPI TestClient with mocked authentication
- `valid_token_headers` - Headers with a valid JWT token
- `invalid_token_headers` - Headers with an invalid JWT token
- `session` - Database session for testing
- `mock_token_payload` - Mock JWT token payload for testing

## Continuous Integration

Tests are designed to run in CI/CD pipelines and include:
- Fast execution (using in-memory database)
- Comprehensive coverage (all endpoints and scenarios)
- Clear error reporting
- Consistent test results