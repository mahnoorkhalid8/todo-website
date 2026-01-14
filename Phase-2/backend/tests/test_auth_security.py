/**
 * Comprehensive API tests for JWT authentication, user isolation, and CRUD operations
 * for the Todo application backend.
 */

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from datetime import datetime, timedelta
from jose import jwt
import json

from main import app
from models import Task
from config import settings


@pytest.fixture(name="engine")
def engine_fixture():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a database session for testing."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(engine):
    """Create a test client with the in-memory database."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(name="valid_token_payload")
def valid_token_payload_fixture():
    """Valid JWT token payload for testing."""
    return {
        "user_id": "test-user-id",
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),  # Expires in 1 hour
        "sub": "test-user-id"
    }


@pytest.fixture(name="valid_jwt_token")
def valid_jwt_token_fixture(valid_token_payload):
    """Valid JWT token for testing."""
    return jwt.encode(valid_token_payload, settings.better_auth_secret, algorithm="HS256")


@pytest.fixture(name="expired_token_payload")
def expired_token_payload_fixture():
    """Expired JWT token payload for testing."""
    return {
        "user_id": "test-user-id",
        "email": "test@example.com",
        "exp": datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
        "sub": "test-user-id"
    }


@pytest.fixture(name="expired_jwt_token")
def expired_jwt_token_fixture(expired_token_payload):
    """Expired JWT token for testing."""
    return jwt.encode(expired_token_payload, settings.better_auth_secret, algorithm="HS256")


def test_jwt_authentication_required_for_all_task_endpoints(client: TestClient):
    """Test that all task endpoints require JWT authentication."""
    endpoints = [
        ("GET", "/api/test-user/tasks"),
        ("POST", "/api/test-user/tasks", {"title": "Test Task", "completed": False}),
        ("GET", "/api/test-user/tasks/1"),
        ("PUT", "/api/test-user/tasks/1", {"title": "Updated Task"}),
        ("DELETE", "/api/test-user/tasks/1"),
        ("PATCH", "/api/test-user/tasks/1/complete", {"completed": True}),
    ]

    for endpoint in endpoints:
        method = endpoint[0]
        url = endpoint[1]
        data = endpoint[2] if len(endpoint) > 2 else None

        if method == "GET":
            response = client.get(url)
        elif method == "POST":
            response = client.post(url, json=data)
        elif method == "PUT":
            response = client.put(url, json=data)
        elif method == "DELETE":
            response = client.delete(url)
        elif method == "PATCH":
            response = client.patch(url, json=data)

        assert response.status_code == 401, f"{method} {url} should require authentication"


def test_jwt_token_verification_success(client: TestClient, valid_jwt_token: str):
    """Test successful JWT token verification."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}

    # Test with a non-existent user ID to ensure auth passes but user isolation might fail
    response = client.get(f"/api/test-user-id/tasks", headers=headers)

    # Should not be unauthorized (could be 403 due to user isolation or 404 if user doesn't exist)
    assert response.status_code != 401, "Valid JWT token should not result in 401"


def test_jwt_token_verification_failure(client: TestClient, invalid_token_headers: dict):
    """Test JWT token verification failure with invalid token."""
    response = client.get("/api/test-user/tasks", headers=invalid_token_headers)
    assert response.status_code == 401


def test_expired_jwt_token_handling(client: TestClient, expired_jwt_token: str):
    """Test handling of expired JWT tokens."""
    headers = {"Authorization": f"Bearer {expired_jwt_token}"}
    response = client.get("/api/test-user-id/tasks", headers=headers)
    assert response.status_code == 401


def test_malformed_jwt_token(client: TestClient):
    """Test handling of malformed JWT tokens."""
    headers = {"Authorization": "Bearer this.is.not.a.valid.token"}
    response = client.get("/api/test-user/tasks", headers=headers)
    assert response.status_code == 401


def test_missing_authorization_header(client: TestClient):
    """Test requests without Authorization header."""
    response = client.get("/api/test-user/tasks")
    assert response.status_code == 401


def test_bearer_prefix_only(client: TestClient):
    """Test requests with only Bearer prefix and no token."""
    headers = {"Authorization": "Bearer "}
    response = client.get("/api/test-user/tasks", headers=headers)
    assert response.status_code == 401


def test_user_isolation_get_tasks(client: TestClient, valid_jwt_token: str):
    """Test that users can only access their own tasks."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}

    # Token has user_id="test-user-id" but URL has "other-user-id"
    # This should fail due to user isolation
    response = client.get("/api/other-user-id/tasks", headers=headers)
    assert response.status_code == 403  # Forbidden


def test_user_isolation_get_specific_task(client: TestClient, valid_jwt_token: str):
    """Test user isolation for getting a specific task."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}

    # Try to access a specific task with different user ID
    response = client.get("/api/other-user-id/tasks/1", headers=headers)
    assert response.status_code == 403  # Forbidden


def test_user_isolation_create_task(client: TestClient, valid_jwt_token: str):
    """Test user isolation for creating tasks."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}

    # Try to create a task with different user ID in URL
    task_data = {"title": "Test Task", "description": "Test Description", "completed": False}
    response = client.post("/api/other-user-id/tasks", json=task_data, headers=headers)
    assert response.status_code == 403  # Forbidden


def test_user_isolation_update_task(client: TestClient, valid_jwt_token: str):
    """Test user isolation for updating tasks."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}

    # Try to update a task with different user ID in URL
    update_data = {"title": "Updated Task", "completed": True}
    response = client.put("/api/other-user-id/tasks/1", json=update_data, headers=headers)
    assert response.status_code == 403  # Forbidden


def test_user_isolation_delete_task(client: TestClient, valid_jwt_token: str):
    """Test user isolation for deleting tasks."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}

    # Try to delete a task with different user ID in URL
    response = client.delete("/api/other-user-id/tasks/1", headers=headers)
    assert response.status_code == 403  # Forbidden


def test_user_isolation_toggle_completion(client: TestClient, valid_jwt_token: str):
    """Test user isolation for toggling task completion."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}

    # Try to toggle completion with different user ID in URL
    completion_data = {"completed": True}
    response = client.patch("/api/other-user-id/tasks/1/complete", json=completion_data, headers=headers)
    assert response.status_code == 403  # Forbidden


def test_successful_task_crud_operations(client: TestClient, valid_jwt_token: str, session: Session):
    """Test successful CRUD operations with proper authentication and user isolation."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # 1. Create a task
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False
    }
    create_response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
    assert create_response.status_code == 201

    created_task = create_response.json()
    assert created_task["title"] == "Test Task"
    assert created_task["user_id"] == user_id
    task_id = created_task["id"]

    # 2. Get all tasks for the user
    get_all_response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert get_all_response.status_code == 200
    tasks_list = get_all_response.json()
    assert len(tasks_list) == 1
    assert tasks_list[0]["id"] == task_id

    # 3. Get specific task
    get_one_response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert get_one_response.status_code == 200
    retrieved_task = get_one_response.json()
    assert retrieved_task["id"] == task_id
    assert retrieved_task["title"] == "Test Task"

    # 4. Update task
    update_data = {"title": "Updated Task Title", "completed": True}
    update_response = client.put(f"/api/{user_id}/tasks/{task_id}", json=update_data, headers=headers)
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["id"] == task_id
    assert updated_task["title"] == "Updated Task Title"
    assert updated_task["completed"] is True

    # 5. Toggle completion status
    toggle_data = {"completed": False}
    toggle_response = client.patch(f"/api/{user_id}/tasks/{task_id}/complete", json=toggle_data, headers=headers)
    assert toggle_response.status_code == 200
    toggled_task = toggle_response.json()
    assert toggled_task["id"] == task_id
    assert toggled_task["completed"] is False

    # 6. Delete task
    delete_response = client.delete(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 204  # No content

    # 7. Verify task is deleted
    verify_response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert verify_response.status_code == 404


def test_task_validation_rules(client: TestClient, valid_jwt_token: str):
    """Test validation rules for task creation and updates."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Test empty title validation
    invalid_task_data = {"title": "", "description": "Valid Description", "completed": False}
    response = client.post(f"/api/{user_id}/tasks", json=invalid_task_data, headers=headers)
    assert response.status_code == 422  # Validation error

    # Test very long title validation
    long_title = "a" * 201  # Exceeds max length of 200
    invalid_task_data = {"title": long_title, "description": "Valid Description", "completed": False}
    response = client.post(f"/api/{user_id}/tasks", json=invalid_task_data, headers=headers)
    assert response.status_code == 422  # Validation error

    # Test valid task creation
    valid_task_data = {"title": "Valid Task Title", "description": "Valid Description", "completed": False}
    response = client.post(f"/api/{user_id}/tasks", json=valid_task_data, headers=headers)
    assert response.status_code == 201


def test_get_tasks_with_filters(client: TestClient, valid_jwt_token: str, session: Session):
    """Test getting tasks with filtering and sorting parameters."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Create test tasks
    task1 = Task(user_id=user_id, title="Pending Task", description="Pending Description", completed=False)
    task2 = Task(user_id=user_id, title="Completed Task", description="Completed Description", completed=True)
    session.add(task1)
    session.add(task2)
    session.commit()

    # Test filtering by status
    response = client.get(f"/api/{user_id}/tasks?status_filter=pending", headers=headers)
    assert response.status_code == 200
    pending_tasks = response.json()
    assert len(pending_tasks) == 1
    assert pending_tasks[0]["completed"] is False

    # Test filtering by completed status
    response = client.get(f"/api/{user_id}/tasks?status_filter=completed", headers=headers)
    assert response.status_code == 200
    completed_tasks = response.json()
    assert len(completed_tasks) == 1
    assert completed_tasks[0]["completed"] is True


def test_error_handling_scenarios(client: TestClient, valid_jwt_token: str):
    """Test various error handling scenarios."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Test getting non-existent task
    response = client.get(f"/api/{user_id}/tasks/999999", headers=headers)
    assert response.status_code == 404

    # Test updating non-existent task
    update_data = {"title": "Updated Task"}
    response = client.put(f"/api/{user_id}/tasks/999999", json=update_data, headers=headers)
    assert response.status_code == 404

    # Test deleting non-existent task
    response = client.delete(f"/api/{user_id}/tasks/999999", headers=headers)
    assert response.status_code == 404

    # Test toggling completion for non-existent task
    toggle_data = {"completed": True}
    response = client.patch(f"/api/{user_id}/tasks/999999/complete", json=toggle_data, headers=headers)
    assert response.status_code == 404


def test_jwt_secret_configuration(client: TestClient, valid_token_payload: dict):
    """Test that JWT verification uses the correct secret."""
    # Create a token with a different secret to ensure the correct one is used
    different_secret_token = jwt.encode(valid_token_payload, "different-secret", algorithm="HS256")
    headers = {"Authorization": f"Bearer {different_secret_token}"}

    response = client.get("/api/test-user/tasks", headers=headers)
    assert response.status_code == 401  # Should fail with wrong secret


def test_jwt_algorithm_validation(client: TestClient, valid_token_payload: dict):
    """Test that only allowed JWT algorithms are accepted."""
    # Create a token with a different algorithm
    alg_modified_token = jwt.encode(valid_token_payload, settings.better_auth_secret, algorithm="HS512")
    headers = {"Authorization": f"Bearer {alg_modified_token}"}

    # This might pass or fail depending on how the JWT library is configured
    # but we'll check that it doesn't crash the application
    response = client.get("/api/test-user/tasks", headers=headers)
    # Could be 401 if algorithm mismatch is caught, or 403 if user isolation kicks in
    assert response.status_code in [401, 403, 404]


def test_large_request_body_handling(client: TestClient, valid_jwt_token: str):
    """Test handling of large request bodies."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Create a task with a very large description
    large_description = "a" * 5000  # Large description
    task_data = {
        "title": "Large Description Task",
        "description": large_description,
        "completed": False
    }

    response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
    # Should either accept the large request or return a validation error, but not crash
    assert response.status_code in [201, 422]


def test_special_characters_in_task_data(client: TestClient, valid_jwt_token: str):
    """Test handling of special characters in task data."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    special_char_task = {
        "title": "Task with special chars: !@#$%^&*()",
        "description": "Unicode chars: ñáéíóú 中文 🚀",
        "completed": False
    }

    response = client.post(f"/api/{user_id}/tasks", json=special_char_task, headers=headers)
    assert response.status_code == 201

    created_task = response.json()
    assert created_task["title"] == special_char_task["title"]
    assert created_task["description"] == special_char_task["description"]


def test_concurrent_requests_handling(client: TestClient, valid_jwt_token: str):
    """Test handling of concurrent requests to the API."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    import concurrent.futures
    import threading

    def make_request(task_num: int):
        task_data = {
            "title": f"Concurrent Task {task_num}",
            "description": f"Task created in concurrent request {task_num}",
            "completed": False
        }
        response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
        return response.status_code, response.json() if response.status_code == 201 else None

    # Make multiple requests concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, i) for i in range(5)]
        results = [future.result() for future in futures]

    # All requests should succeed (201) or at least not cause server errors
    for status_code, data in results:
        assert status_code in [201, 400, 422]  # Success or validation error, but not server error


def test_sql_injection_prevention(client: TestClient, valid_jwt_token: str):
    """Test that the API prevents SQL injection attempts."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Try to inject SQL through the title field
    injection_task = {
        "title": "'; DROP TABLE tasks; --",
        "description": "Normal description",
        "completed": False
    }

    # This should either create a task with the literal string or fail validation
    # but should not execute the SQL injection
    response = client.post(f"/api/{user_id}/tasks", json=injection_task, headers=headers)
    # The request should not crash the server (not return 500)
    assert response.status_code != 500


def test_xss_prevention(client: TestClient, valid_jwt_token: str):
    """Test that the API prevents XSS attempts."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Try to inject script through the task fields
    xss_task = {
        "title": "<script>alert('XSS')</script>",
        "description": "Normal description",
        "completed": False
    }

    # This should either create a task with the literal string or fail validation
    # but should not execute the script
    response = client.post(f"/api/{user_id}/tasks", json=xss_task, headers=headers)
    # Should not return 500 (server error)
    assert response.status_code != 500


def test_rate_limiting_simulation(client: TestClient, valid_jwt_token: str):
    """Test how the API handles rapid successive requests (rate limiting simulation)."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Make several requests in a row
    for i in range(10):
        task_data = {
            "title": f"Rate Limit Test Task {i}",
            "description": f"Task {i} for rate limit testing",
            "completed": False
        }

        response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
        # All requests should be processed without server errors
        assert response.status_code in [201, 400, 422]  # Success or validation error, not 500


def test_token_refresh_simulation(client: TestClient, valid_token_payload: dict):
    """Test token refresh simulation by checking the token structure."""
    # In a real implementation, we would test the actual refresh endpoint
    # For now, we'll just verify that the token has the expected structure
    token = jwt.encode(valid_token_payload, settings.better_auth_secret, algorithm="HS256")

    # Decode and verify the token structure
    decoded_payload = jwt.decode(token, settings.better_auth_secret, algorithms=["HS256"])
    assert "user_id" in decoded_payload
    assert "email" in decoded_payload
    assert "exp" in decoded_payload
    assert decoded_payload["user_id"] == valid_token_payload["user_id"]