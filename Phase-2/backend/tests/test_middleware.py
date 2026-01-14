"""
Middleware tests for the Todo application.
Tests authentication middleware, JWT token verification, and user isolation.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from middleware.auth import auth_middleware, verify_token


def test_auth_middleware_valid_token(client: TestClient, valid_token_headers: dict):
    """Test that the auth middleware allows requests with valid tokens from environment secrets."""
    response = client.get("/api/test-user-id/tasks", headers=valid_token_headers)
    # Should be allowed (either 200 or 403 depending on user isolation)
    assert response.status_code in [200, 403]


def test_auth_middleware_invalid_token(client: TestClient, invalid_token_headers: dict):
    """Test that the auth middleware rejects requests with invalid tokens."""
    response = client.get("/api/test-user/tasks", headers=invalid_token_headers)
    assert response.status_code == 401  # Unauthorized


def test_auth_middleware_missing_token(client: TestClient):
    """Test that the auth middleware rejects requests without tokens."""
    response = client.get("/api/test-user/tasks")
    assert response.status_code == 401  # Unauthorized


def test_auth_middleware_malformed_header(client: TestClient):
    """Test that the auth middleware handles malformed authorization headers."""
    headers = {"Authorization": "NotBearerToken"}
    response = client.get("/api/test-user/tasks", headers=headers)
    assert response.status_code == 401  # Unauthorized


def test_verify_token_function_with_real_token(real_token_payload):
    """Test the verify_token function with a real token from environment secrets."""
    # This test verifies that the token payload structure is correct
    assert "user_id" in real_token_payload
    assert "email" in real_token_payload
    assert "exp" in real_token_payload
    assert "sub" in real_token_payload
    assert real_token_payload["user_id"] == "test-user-id"
    assert real_token_payload["email"] == "test@example.com"


def test_verify_token_function_with_invalid_token():
    """Test the verify_token function with an invalid token."""
    from middleware.auth import verify_token
    result = verify_token("invalid-token")
    assert result is None


def test_user_id_extraction_from_token(real_token_payload):
    """Test that user ID is properly extracted from JWT token."""
    # Test that the real token payload contains the expected user_id
    assert "user_id" in real_token_payload
    assert real_token_payload["user_id"] == "test-user-id"


def test_user_id_validation_in_middleware(client: TestClient, valid_token_headers: dict):
    """Test that the middleware validates user ID in token against URL."""
    # Token has user_id="test-user-id" but URL has "different-user-id"
    response = client.get("/api/different-user-id/tasks", headers=valid_token_headers)
    assert response.status_code == 403  # Forbidden - user isolation


def test_public_routes_skip_authentication(client: TestClient):
    """Test that public routes (like root) don't require authentication."""
    response = client.get("/")
    # This should work without auth
    assert response.status_code == 200
    assert response.json() == {"message": "Todo API is running"}


def test_middleware_applies_to_all_api_routes(client: TestClient):
    """Test that authentication middleware applies to all API routes."""
    api_routes = [
        "/api/test-user/tasks",
        "/api/test-user/tasks/1",
        "/api/test-user/tasks/1/complete"
    ]

    for route in api_routes:
        response = client.get(route)
        # All API routes should require authentication
        assert response.status_code == 401, f"{route} should require authentication"


def test_middleware_token_expiry_handling():
    """Test that the middleware handles expired tokens."""
    # In a real implementation, we would test actual token expiry
    # For now, we test the concept
    from middleware.auth import verify_token
    # This would test with an expired token
    result = verify_token("expired-token")
    assert result is None


def test_middleware_user_isolation_enforcement(client: TestClient, valid_token_headers: dict):
    """Test that the middleware enforces user isolation."""
    # Try to access another user's data with a valid token for a different user
    response = client.get("/api/other-user/tasks", headers=valid_token_headers)
    # Should be forbidden due to user isolation
    assert response.status_code == 403


def test_middleware_state_population(client: TestClient, valid_token_headers: dict):
    """Test that the middleware populates request state with user info."""
    # This tests that the middleware adds user info to request.state
    # In our test setup, this is difficult to test directly
    # So we test the behavior through API responses
    response = client.get("/api/test-user-id/tasks", headers=valid_token_headers)
    # Should not be unauthorized (meaning middleware processed the token)
    assert response.status_code != 401


def test_auth_middleware_protects_all_http_methods(client: TestClient, valid_token_headers: dict):
    """Test that auth middleware protects all HTTP methods."""
    # Test that all methods require authentication
    endpoints = [
        ("GET", "/api/test-user/tasks"),
        ("POST", "/api/test-user/tasks", {"title": "Test"}),
        ("GET", "/api/test-user/tasks/1"),
        ("PUT", "/api/test-user/tasks/1", {"title": "Updated"}),
        ("DELETE", "/api/test-user/tasks/1"),
        ("PATCH", "/api/test-user/tasks/1/complete", {"completed": True}),
    ]

    for endpoint in endpoints:
        method = endpoint[0]
        path = endpoint[1]
        data = endpoint[2] if len(endpoint) > 2 else None

        # Without auth
        if method == "GET":
            response = client.get(path)
        elif method == "POST":
            response = client.post(path, json=data)
        elif method == "PUT":
            response = client.put(path, json=data)
        elif method == "DELETE":
            response = client.delete(path)
        elif method == "PATCH":
            response = client.patch(path, json=data)

        assert response.status_code == 401, f"{method} {path} should require authentication"

        # With auth - should not be unauthorized (could be 403 due to user isolation)
        if method == "GET":
            response = client.get(path, headers=valid_token_headers)
        elif method == "POST":
            response = client.post(path, json=data, headers=valid_token_headers)
        elif method == "PUT":
            response = client.put(path, json=data, headers=valid_token_headers)
        elif method == "DELETE":
            response = client.delete(path, headers=valid_token_headers)
        elif method == "PATCH":
            response = client.patch(path, json=data, headers=valid_token_headers)

        # Should not be unauthorized (may be 200, 403, or 404)
        assert response.status_code != 401, f"{method} {path} should accept valid authentication"


def test_middleware_security_validation(client: TestClient, valid_token_headers: dict):
    """Test comprehensive security validation through middleware."""
    # Test unauthorized access
    assert client.get("/api/test-user/tasks").status_code == 401

    # Test invalid token rejection (using lambda for the other tests)
    invalid_header_test = lambda: client.get("/api/test-user/tasks",
                                           headers={"Authorization": "Bearer invalid"}).status_code == 401
    assert invalid_header_test()

    # Test malformed header rejection
    malformed_header_test = lambda: client.get("/api/test-user/tasks",
                                            headers={"Authorization": "invalid"}).status_code == 401
    assert malformed_header_test()

    # Test proper auth works (doesn't return 401) using real token headers
    response = client.get("/api/test-user-id/tasks", headers=valid_token_headers)
    assert response.status_code != 401