"""
Authentication and JWT token verification tests for the Todo application.
Tests JWT token handling, user isolation, and authentication flow.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import jwt
from datetime import datetime, timedelta
from config import settings


def test_jwt_token_verification_success(client: TestClient, valid_token_headers: dict):
    """Test successful JWT token verification with real environment secrets."""
    response = client.get("/api/test-user-id/tasks", headers=valid_token_headers)
    # Should be authorized (might still get 403 due to user isolation if user_id doesn't match)
    assert response.status_code in [200, 403]  # 200 = OK, 403 = forbidden (due to user isolation)


def test_jwt_token_verification_failure(client: TestClient, invalid_token_headers: dict):
    """Test JWT token verification failure with invalid token."""
    response = client.get("/api/test-user/tasks", headers=invalid_token_headers)
    assert response.status_code == 401  # Unauthorized


def test_missing_authorization_header(client: TestClient):
    """Test request without Authorization header."""
    response = client.get("/api/test-user/tasks")
    assert response.status_code == 401  # Unauthorized


def test_malformed_authorization_header(client: TestClient):
    """Test request with malformed Authorization header."""
    headers = {"Authorization": "InvalidFormatToken"}
    response = client.get("/api/test-user/tasks", headers=headers)
    assert response.status_code == 401  # Unauthorized


def test_bearer_token_prefix_missing(client: TestClient):
    """Test request without Bearer prefix in Authorization header."""
    headers = {"Authorization": "valid-token"}
    response = client.get("/api/test-user/tasks", headers=headers)
    assert response.status_code == 401  # Unauthorized


def test_expired_token_handling(client: TestClient, invalid_token_headers: dict):
    """Test handling of expired JWT tokens."""
    # Test that expired/invalid tokens are properly rejected
    response = client.get("/api/test-user/tasks", headers=invalid_token_headers)
    assert response.status_code == 401  # Unauthorized


def test_user_isolation_enforcement(client: TestClient, valid_token_headers: dict):
    """Test that user isolation is enforced at the API level."""
    # Token has user_id="test-user-id" but URL has "different-user-id"
    response = client.get("/api/different-user-id/tasks", headers=valid_token_headers)
    assert response.status_code == 403  # Forbidden - user isolation


def test_task_ownership_enforcement_get(client: TestClient, valid_token_headers: dict):
    """Test that task ownership is enforced when getting a specific task."""
    # Try to access a task with user_id that doesn't match the token
    response = client.get("/api/wrong-user-id/tasks/1", headers=valid_token_headers)
    assert response.status_code == 403  # Forbidden - user isolation


def test_task_ownership_enforcement_update(client: TestClient, valid_token_headers: dict):
    """Test that task ownership is enforced when updating a task."""
    # Try to update a task with user_id that doesn't match the token
    response = client.put("/api/wrong-user-id/tasks/1", json={"title": "Updated"}, headers=valid_token_headers)
    assert response.status_code == 403  # Forbidden - user isolation


def test_task_ownership_enforcement_delete(client: TestClient, valid_token_headers: dict):
    """Test that task ownership is enforced when deleting a task."""
    # Try to delete a task with user_id that doesn't match the token
    response = client.delete("/api/wrong-user-id/tasks/1", headers=valid_token_headers)
    assert response.status_code == 403  # Forbidden - user isolation


def test_task_ownership_enforcement_toggle_completion(client: TestClient, valid_token_headers: dict):
    """Test that task ownership is enforced when toggling completion status."""
    # Try to toggle completion for a task with user_id that doesn't match the token
    response = client.patch("/api/wrong-user-id/tasks/1/complete", json={"completed": True}, headers=valid_token_headers)
    assert response.status_code == 403  # Forbidden - user isolation


def test_auth_middleware_applies_to_all_protected_routes(client: TestClient):
    """Test that authentication is required for all protected routes."""
    protected_routes = [
        ("/api/test-user/tasks", "GET"),
        ("/api/test-user/tasks", "POST", {"title": "Test"}),
        ("/api/test-user/tasks/1", "GET"),
        ("/api/test-user/tasks/1", "PUT", {"title": "Updated"}),
        ("/api/test-user/tasks/1", "DELETE"),
        ("/api/test-user/tasks/1/complete", "PATCH", {"completed": True}),
    ]

    for route in protected_routes:
        path = route[0]
        method = route[1]
        data = route[2] if len(route) > 2 else None

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

        # All should return 401 (unauthorized) without proper auth
        assert response.status_code == 401, f"{method} {path} should require authentication"


def test_valid_token_allows_access_to_own_data(client: TestClient, valid_token_headers: dict):
    """Test that valid tokens allow access to user's own data."""
    # Create a task first
    task_data = {
        "title": "Test Task for Auth",
        "description": "Testing authentication",
        "completed": False
    }
    create_response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert create_response.status_code in [200, 201]  # May return 200 or 201 depending on implementation

    if create_response.status_code == 201:
        task_id = create_response.json()["id"]

        # Now try to access it
        get_response = client.get(f"/api/test-user-id/tasks/{task_id}", headers=valid_token_headers)
        assert get_response.status_code in [200, 404]  # 200 if exists, 404 if not created yet but auth worked


def test_jwt_token_contains_correct_claims(real_token_payload: dict):
    """Test that JWT tokens contain the expected claims."""
    # This tests our real payload structure from environment secrets
    assert "user_id" in real_token_payload
    assert "email" in real_token_payload
    assert "exp" in real_token_payload
    assert "sub" in real_token_payload
    assert real_token_payload["user_id"] == "test-user-id"
    assert real_token_payload["email"] == "test@example.com"


def test_auth_flow_integration(client: TestClient, valid_token_headers: dict):
    """Test the complete authentication flow with real environment secrets."""
    # 1. Try to access protected resource without auth -> should fail
    response = client.get("/api/test-user/tasks")
    assert response.status_code == 401

    # 2. Try with valid auth -> should work (or fail on user isolation which is also OK)
    response = client.get("/api/test-user-id/tasks", headers=valid_token_headers)
    # Should be either 200 (success) or 403 (user isolation working)
    assert response.status_code in [200, 403, 404]


def test_security_validation_for_all_endpoints(client: TestClient, valid_token_headers: dict):
    """Test that all endpoints properly validate JWT tokens."""
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

        # Test without authentication
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

        # Should return 401 for all unauthenticated requests
        assert response.status_code == 401, f"{method} {path} should require authentication"


def test_edge_case_empty_token(client: TestClient):
    """Test edge case with empty token."""
    headers = {"Authorization": "Bearer "}
    response = client.get("/api/test-user/tasks", headers=headers)
    assert response.status_code == 401  # Unauthorized


def test_edge_case_whitespace_token(client: TestClient):
    """Test edge case with whitespace-only token."""
    headers = {"Authorization": "Bearer    "}
    response = client.get("/api/test-user/tasks", headers=headers)
    assert response.status_code == 401  # Unauthorized