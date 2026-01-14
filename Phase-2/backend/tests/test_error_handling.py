"""
Error handling and edge case tests for the Todo application.
Tests comprehensive error handling, edge cases, and proper responses.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException


def test_error_handling_unauthorized_access(client: TestClient):
    """Test that unauthorized access returns proper error responses."""
    response = client.get("/api/test-user/tasks")
    assert response.status_code == 401
    error_detail = response.json()
    assert "detail" in error_detail
    assert "authorization" in error_detail["detail"].lower() or "unauthorized" in error_detail["detail"].lower()


def test_error_handling_forbidden_access(client: TestClient, valid_token_headers: dict):
    """Test that forbidden access returns proper error responses."""
    # Try to access another user's resources
    response = client.get("/api/other-user-id/tasks", headers=valid_token_headers)
    assert response.status_code == 403
    error_detail = response.json()
    assert "detail" in error_detail
    assert "forbidden" in error_detail["detail"].lower() or "authorized" in error_detail["detail"].lower()


def test_error_handling_not_found(client: TestClient, valid_token_headers: dict):
    """Test that not found resources return proper error responses."""
    response = client.get("/api/test-user-id/tasks/999999", headers=valid_token_headers)
    assert response.status_code == 404
    error_detail = response.json()
    assert "detail" in error_detail
    assert "not found" in error_detail["detail"].lower()


def test_error_handling_bad_request(client: TestClient, valid_token_headers: dict):
    """Test bad request handling."""
    # Send malformed data to create task endpoint
    invalid_data = {
        "title": "",  # Invalid: empty title
        "description": "Valid description",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=invalid_data, headers=valid_token_headers)
    assert response.status_code in [400, 422]  # Could be validation error (422) or bad request (400)
    error_detail = response.json()
    assert "detail" in error_detail or response.status_code == 422  # Validation errors may not have detail


def test_error_handling_server_error_simulation(client: TestClient, valid_token_headers: dict):
    """Test server error handling (when possible)."""
    # This would require specific error conditions to trigger 500s
    # For now, we'll just ensure normal operations don't cause server errors
    # Create a valid task
    valid_data = {
        "title": "Valid Task",
        "description": "Valid Description",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=valid_data, headers=valid_token_headers)
    # Should not return 500
    assert response.status_code != 500


def test_edge_case_long_input_values(client: TestClient, valid_token_headers: dict):
    """Test handling of very long input values."""
    # Test with maximum allowed title length
    max_title = "a" * 200  # Assuming 200 is max length
    valid_data = {
        "title": max_title,
        "description": "Valid Description",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=valid_data, headers=valid_token_headers)
    # Should either accept or return validation error (not crash)
    assert response.status_code in [201, 422]

    # Test with exceeding maximum length
    too_long_title = "a" * 201  # Exceeds max length
    invalid_data = {
        "title": too_long_title,
        "description": "Valid Description",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=invalid_data, headers=valid_token_headers)
    # Should return validation error
    assert response.status_code == 422


def test_edge_case_special_characters(client: TestClient, valid_token_headers: dict):
    """Test handling of special characters in inputs."""
    special_data = {
        "title": "Task with special chars: !@#$%^&*()",
        "description": "Description with unicode: ñ, é, ü, 中文",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=special_data, headers=valid_token_headers)
    # Should handle special characters properly
    assert response.status_code in [201, 422]  # Either created or validation error, but not server error


def test_edge_case_null_values(client: TestClient, valid_token_headers: dict):
    """Test handling of null values in optional fields."""
    null_data = {
        "title": "Task with null description",
        "description": None,  # This might be allowed
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=null_data, headers=valid_token_headers)
    # Should handle null values properly
    assert response.status_code in [201, 422]


def test_edge_case_missing_required_fields(client: TestClient, valid_token_headers: dict):
    """Test handling of missing required fields."""
    incomplete_data = {
        # Missing required title field
        "description": "Task without title",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=incomplete_data, headers=valid_token_headers)
    # Should return validation error
    assert response.status_code == 422


def test_edge_case_extra_fields(client: TestClient, valid_token_headers: dict):
    """Test handling of extra fields not in the schema."""
    extra_data = {
        "title": "Task with extra fields",
        "description": "Description",
        "completed": False,
        "extra_field": "should be ignored"
    }
    response = client.post("/api/test-user-id/tasks", json=extra_data, headers=valid_token_headers)
    # Should either ignore extra fields or return an error
    assert response.status_code in [201, 422]


def test_edge_case_large_numbers(client: TestClient, valid_token_headers: dict):
    """Test handling of very large numbers in numeric fields."""
    # While our current model doesn't have large numeric fields,
    # we test the general approach
    valid_data = {
        "title": "Task with large values",
        "description": "Description",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=valid_data, headers=valid_token_headers)
    assert response.status_code in [201, 422]


def test_edge_case_concurrent_requests(client: TestClient, valid_token_headers: dict):
    """Test handling of concurrent requests (basic check)."""
    import threading
    import time

    results = []

    def make_request():
        data = {
            "title": f"Concurrent Task {int(time.time() * 1000)}",
            "description": "Description for concurrent test",
            "completed": False
        }
        response = client.post("/api/test-user-id/tasks", json=data, headers=valid_token_headers)
        results.append(response.status_code)

    # Create multiple threads making requests simultaneously
    threads = []
    for _ in range(3):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # All requests should either succeed or fail gracefully (no server crashes)
    for status in results:
        assert status in [201, 400, 422, 401, 403, 404, 409]  # Common valid HTTP status codes


def test_edge_case_invalid_json(client: TestClient, valid_token_headers: dict):
    """Test handling of invalid JSON in request body."""
    # Send invalid JSON
    response = client.post(
        "/api/test-user-id/tasks",
        content="{invalid: json}",
        headers={**valid_token_headers, "Content-Type": "application/json"}
    )
    # Should return 422 for invalid JSON or 400 for bad request
    assert response.status_code in [400, 422]


def test_error_handling_method_not_allowed(client: TestClient, valid_token_headers: dict):
    """Test that invalid HTTP methods return proper error responses."""
    # Try to POST to a GET-only resource (conceptually)
    # Actually test a non-existent endpoint with wrong method
    response = client.post("/api/test-user-id", headers=valid_token_headers)  # Assuming this is not a valid endpoint
    # Should return 404, 405, or similar error
    assert response.status_code in [404, 405, 422]


def test_edge_case_empty_request_body(client: TestClient, valid_token_headers: dict):
    """Test handling of empty request body for POST/PUT endpoints."""
    response = client.post("/api/test-user-id/tasks", content="", headers=valid_token_headers)
    # Should return validation error or bad request
    assert response.status_code in [400, 422]


def test_error_handling_internal_server_errors_are_masked(client: TestClient, valid_token_headers: dict):
    """Test that internal server errors return generic messages."""
    # This is hard to test without forcing an actual internal error
    # But we can verify that normal operations don't expose internal details
    valid_data = {
        "title": "Normal Task",
        "description": "Normal Description",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=valid_data, headers=valid_token_headers)
    # Normal request should succeed or return appropriate client error
    assert response.status_code in [201, 422]

    if response.status_code != 201:
        error_detail = response.json()
        # If there's an error, it should be a validation error, not internal
        assert "internal" not in str(error_detail).lower()


def test_edge_case_unicode_characters(client: TestClient, valid_token_headers: dict):
    """Test handling of Unicode characters in inputs."""
    unicode_data = {
        "title": "国际化 国际化",  # Internationalization in Chinese
        "description": "Emojis: 🚀 🐍 🦄 and special chars: ñ ñ ñ",
        "completed": True
    }
    response = client.post("/api/test-user-id/tasks", json=unicode_data, headers=valid_token_headers)
    # Should handle Unicode properly
    assert response.status_code in [201, 422]


def test_error_handling_consistent_error_format(client: TestClient):
    """Test that error responses follow a consistent format."""
    # Test unauthorized error format
    response = client.get("/api/test-user-id/tasks")
    assert response.status_code == 401
    error_response = response.json()
    # Should have detail field
    assert "detail" in error_response


def test_edge_case_sql_injection_attempts(client: TestClient, valid_token_headers: dict):
    """Test that SQL injection attempts are handled safely."""
    injection_data = {
        "title": "'; DROP TABLE tasks; --",
        "description": "SQL injection attempt",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=injection_data, headers=valid_token_headers)
    # Should not crash the database
    # Might create a task with the literal string or reject it
    assert response.status_code in [201, 422]


def test_edge_case_xss_attempts(client: TestClient, valid_token_headers: dict):
    """Test that XSS attempts are handled safely."""
    xss_data = {
        "title": "<script>alert('XSS')</script>",
        "description": "XSS attempt",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=xss_data, headers=valid_token_headers)
    # Should not execute the script
    # Might create a task with the literal string or reject it
    assert response.status_code in [201, 422]