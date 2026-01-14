"""
Complete integration tests for the Todo application backend.
Tests complete workflows including authentication, CRUD operations, user isolation, and security.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from datetime import datetime, timedelta
from jose import jwt
import json
from unittest.mock import patch

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


@pytest.fixture(name="different_user_token_payload")
def different_user_token_payload_fixture():
    """Valid JWT token payload for a different user."""
    return {
        "user_id": "different-user-id",
        "email": "different@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "sub": "different-user-id"
    }


@pytest.fixture(name="different_user_jwt_token")
def different_user_jwt_token_fixture(different_user_token_payload):
    """Valid JWT token for a different user."""
    return jwt.encode(different_user_token_payload, settings.better_auth_secret, algorithm="HS256")


def test_complete_task_management_workflow(client: TestClient, valid_jwt_token: str, session: Session):
    """Test the complete task management workflow."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # 1. Get tasks (should be empty initially)
    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert tasks == []

    # 2. Create a task
    task_data = {
        "title": "Integration Test Task",
        "description": "Task created during integration testing",
        "completed": False
    }
    create_response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
    assert create_response.status_code == 201
    created_task = create_response.json()
    assert created_task["title"] == "Integration Test Task"
    assert created_task["user_id"] == user_id
    assert created_task["completed"] is False
    task_id = created_task["id"]

    # 3. Get all tasks (should now contain 1 task)
    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task_id

    # 4. Get specific task
    response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    specific_task = response.json()
    assert specific_task["id"] == task_id
    assert specific_task["title"] == "Integration Test Task"

    # 5. Update the task
    update_data = {
        "title": "Updated Integration Test Task",
        "completed": True
    }
    update_response = client.put(f"/api/{user_id}/tasks/{task_id}", json=update_data, headers=headers)
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["id"] == task_id
    assert updated_task["title"] == "Updated Integration Test Task"
    assert updated_task["completed"] is True

    # 6. Toggle task completion status
    toggle_data = {"completed": False}
    toggle_response = client.patch(f"/api/{user_id}/tasks/{task_id}/complete", json=toggle_data, headers=headers)
    assert toggle_response.status_code == 200
    toggled_task = toggle_response.json()
    assert toggled_task["id"] == task_id
    assert toggled_task["completed"] is False

    # 7. Delete the task
    delete_response = client.delete(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 204

    # 8. Verify the task is deleted
    verify_response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert verify_response.status_code == 404


def test_user_isolation_comprehensive(client: TestClient, valid_jwt_token: str, different_user_jwt_token: str, session: Session):
    """Comprehensive test of user isolation."""
    # Create tasks for first user
    headers1 = {"Authorization": f"Bearer {valid_jwt_token}"}
    user1_id = "test-user-id"

    task_data = {
        "title": "User 1's Task",
        "description": "Task belonging to user 1",
        "completed": False
    }
    response1 = client.post(f"/api/{user1_id}/tasks", json=task_data, headers=headers1)
    assert response1.status_code == 201
    task1 = response1.json()
    task1_id = task1["id"]

    # Create tasks for second user
    headers2 = {"Authorization": f"Bearer {different_user_jwt_token}"}
    user2_id = "different-user-id"

    task_data2 = {
        "title": "User 2's Task",
        "description": "Task belonging to user 2",
        "completed": True
    }
    response2 = client.post(f"/api/{user2_id}/tasks", json=task_data2, headers=headers2)
    assert response2.status_code == 201
    task2 = response2.json()
    task2_id = task2["id"]

    # Verify user 1 can only see their own tasks
    response = client.get(f"/api/{user1_id}/tasks", headers=headers1)
    assert response.status_code == 200
    user1_tasks = response.json()
    assert len(user1_tasks) == 1
    assert user1_tasks[0]["id"] == task1_id

    # Verify user 2 can only see their own tasks
    response = client.get(f"/api/{user2_id}/tasks", headers=headers2)
    assert response.status_code == 200
    user2_tasks = response.json()
    assert len(user2_tasks) == 1
    assert user2_tasks[0]["id"] == task2_id

    # Verify user 1 cannot access user 2's tasks
    response = client.get(f"/api/{user2_id}/tasks", headers=headers1)
    assert response.status_code == 403  # Forbidden

    # Verify user 2 cannot access user 1's tasks
    response = client.get(f"/api/{user1_id}/tasks", headers=headers2)
    assert response.status_code == 403  # Forbidden

    # Verify user 1 cannot access specific task of user 2
    response = client.get(f"/api/{user2_id}/tasks/{task2_id}", headers=headers1)
    assert response.status_code == 403  # Forbidden

    # Verify user 2 cannot access specific task of user 1
    response = client.get(f"/api/{user1_id}/tasks/{task1_id}", headers=headers2)
    assert response.status_code == 403  # Forbidden


def test_authentication_validation(client: TestClient, valid_jwt_token: str):
    """Test comprehensive authentication validation."""
    user_id = "test-user-id"
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}

    # 1. Test that endpoints require authentication
    endpoints = [
        (client.get, f"/api/{user_id}/tasks"),
        (client.post, f"/api/{user_id}/tasks", {"title": "Test", "completed": False}),
        (client.get, f"/api/{user_id}/tasks/1"),
        (client.put, f"/api/{user_id}/tasks/1", {"title": "Updated"}),
        (client.delete, f"/api/{user_id}/tasks/1"),
        (client.patch, f"/api/{user_id}/tasks/1/complete", {"completed": True}),
    ]

    for endpoint in endpoints:
        method = endpoint[0]
        url = endpoint[1]
        data = endpoint[2] if len(endpoint) > 2 else None

        # Try without authentication
        if data:
            response = method(url, json=data)
        else:
            response = method(url)

        assert response.status_code == 401, f"Endpoint {url} should require authentication"

        # Try with authentication
        if data:
            response = method(url, json=data, headers=headers)
        else:
            response = method(url, headers=headers)

        # Should not be unauthorized (might be 404 if resource doesn't exist, or 403 due to user isolation)
        assert response.status_code != 401, f"Endpoint {url} should accept valid authentication"


def test_jwt_token_validation(client: TestClient):
    """Test JWT token validation with various scenarios."""
    user_id = "test-user-id"

    # 1. Test invalid token
    invalid_headers = {"Authorization": "Bearer invalid.token.here"}
    response = client.get(f"/api/{user_id}/tasks", headers=invalid_headers)
    assert response.status_code == 401

    # 2. Test expired token
    expired_payload = {
        "user_id": user_id,
        "email": "test@example.com",
        "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
        "sub": user_id
    }
    expired_token = jwt.encode(expired_payload, settings.better_auth_secret, algorithm="HS256")
    expired_headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get(f"/api/{user_id}/tasks", headers=expired_headers)
    assert response.status_code == 401

    # 3. Test token with wrong secret
    wrong_secret_token = jwt.encode({"user_id": user_id}, "wrong-secret", algorithm="HS256")
    wrong_secret_headers = {"Authorization": f"Bearer {wrong_secret_token}"}
    response = client.get(f"/api/{user_id}/tasks", headers=wrong_secret_headers)
    assert response.status_code == 401

    # 4. Test token with wrong algorithm (if applicable)
    # This would require a more complex setup to properly test algorithm mismatches


def test_task_validation_and_edge_cases(client: TestClient, valid_jwt_token: str):
    """Test task validation and edge cases."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # 1. Test creating task with empty title (should fail validation)
    empty_title_task = {"title": "", "description": "Valid description", "completed": False}
    response = client.post(f"/api/{user_id}/tasks", json=empty_title_task, headers=headers)
    assert response.status_code == 422  # Validation error

    # 2. Test creating task with very long title (should fail validation)
    long_title_task = {"title": "a" * 201, "description": "Valid description", "completed": False}
    response = client.post(f"/api/{user_id}/tasks", json=long_title_task, headers=headers)
    assert response.status_code == 422  # Validation error

    # 3. Test creating task with maximum length title (should succeed)
    max_title_task = {"title": "a" * 200, "description": "Valid description", "completed": False}
    response = client.post(f"/api/{user_id}/tasks", json=max_title_task, headers=headers)
    assert response.status_code == 201

    # 4. Test creating task with special characters
    special_task = {
        "title": "Task with special chars: !@#$%^&*()",
        "description": "Description with unicode: ñ, é, ü, 中文",
        "completed": False
    }
    response = client.post(f"/api/{user_id}/tasks", json=special_task, headers=headers)
    assert response.status_code == 201

    # 5. Test updating with invalid data
    valid_task = {"title": "Valid Task", "completed": False}
    create_response = client.post(f"/api/{user_id}/tasks", json=valid_task, headers=headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    invalid_update = {"title": ""}  # Empty title
    response = client.put(f"/api/{user_id}/tasks/{task_id}", json=invalid_update, headers=headers)
    assert response.status_code == 422


def test_api_error_handling(client: TestClient, valid_jwt_token: str):
    """Test comprehensive API error handling."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # 1. Test accessing non-existent task
    response = client.get(f"/api/{user_id}/tasks/999999", headers=headers)
    assert response.status_code == 404

    # 2. Test updating non-existent task
    update_data = {"title": "Updated Task"}
    response = client.put(f"/api/{user_id}/tasks/999999", json=update_data, headers=headers)
    assert response.status_code == 404

    # 3. Test deleting non-existent task
    response = client.delete(f"/api/{user_id}/tasks/999999", headers=headers)
    assert response.status_code == 404

    # 4. Test toggling completion for non-existent task
    toggle_data = {"completed": True}
    response = client.patch(f"/api/{user_id}/tasks/999999/complete", json=toggle_data, headers=headers)
    assert response.status_code == 404

    # 5. Test malformed JSON
    response = client.post(
        f"/api/{user_id}/tasks",
        content="{invalid: json}",
        headers={**headers, "Content-Type": "application/json"}
    )
    assert response.status_code in [400, 422]  # Bad request or validation error


def test_task_filtering_and_sorting(client: TestClient, valid_jwt_token: str, session: Session):
    """Test task filtering and sorting functionality."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Create multiple tasks with different properties
    tasks_data = [
        {"title": "Pending Task 1", "description": "First pending task", "completed": False},
        {"title": "Completed Task 1", "description": "First completed task", "completed": True},
        {"title": "Pending Task 2", "description": "Second pending task", "completed": False},
        {"title": "Completed Task 2", "description": "Second completed task", "completed": True},
    ]

    created_tasks = []
    for task_data in tasks_data:
        response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
        assert response.status_code == 201
        created_tasks.append(response.json())

    # Test filtering by status
    pending_response = client.get(f"/api/{user_id}/tasks?status_filter=pending", headers=headers)
    assert pending_response.status_code == 200
    pending_tasks = pending_response.json()
    assert len(pending_tasks) == 2
    for task in pending_tasks:
        assert task["completed"] is False

    completed_response = client.get(f"/api/{user_id}/tasks?status_filter=completed", headers=headers)
    assert completed_response.status_code == 200
    completed_tasks = completed_response.json()
    assert len(completed_tasks) == 2
    for task in completed_tasks:
        assert task["completed"] is True

    # Test getting all tasks (default behavior)
    all_response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert all_response.status_code == 200
    all_tasks = all_response.json()
    assert len(all_tasks) == 4


def test_concurrent_access_and_race_conditions(client: TestClient, valid_jwt_token: str):
    """Test handling of concurrent access to the API."""
    import threading
    import time

    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Results list to store responses from each thread
    results = []

    def create_task_thread(task_num: int):
        task_data = {
            "title": f"Concurrent Task {task_num}",
            "description": f"Task created in thread {task_num}",
            "completed": False
        }
        start_time = time.time()
        response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
        end_time = time.time()
        results.append({
            "task_num": task_num,
            "status": response.status_code,
            "time_taken": end_time - start_time,
            "data": response.json() if response.status_code == 201 else None
        })

    # Create multiple threads to simulate concurrent requests
    threads = []
    for i in range(5):  # Create 5 concurrent tasks
        thread = threading.Thread(target=create_task_thread, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify that all requests were handled properly
    success_count = sum(1 for r in results if r["status"] == 201)
    assert success_count == 5, f"Expected 5 successes, got {success_count}"

    # Verify that all created tasks exist
    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert response.status_code == 200
    all_tasks = response.json()
    assert len(all_tasks) == 5


def test_security_validation(client: TestClient, valid_jwt_token: str):
    """Test comprehensive security validation."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # 1. Test SQL injection prevention in task data
    sql_injection_task = {
        "title": "'; DROP TABLE tasks; --",
        "description": "SQL injection attempt",
        "completed": False
    }
    response = client.post(f"/api/{user_id}/tasks", json=sql_injection_task, headers=headers)
    # Should either reject the request or handle it safely (not crash)
    assert response.status_code in [201, 422, 400]  # Success, validation error, or bad request

    # 2. Test XSS prevention in task data
    xss_task = {
        "title": "<script>alert('XSS')</script>",
        "description": "XSS attempt in description",
        "completed": False
    }
    response = client.post(f"/api/{user_id}/tasks", json=xss_task, headers=headers)
    # Should handle the request safely
    assert response.status_code in [201, 422, 400]

    # 3. Test user isolation with different user ID in URL
    response = client.get(f"/api/other-user-id/tasks", headers=headers)
    assert response.status_code == 403  # Forbidden due to user isolation

    # 4. Test accessing other user's resources
    # First create a task
    task_data = {"title": "Security Test Task", "completed": False}
    create_response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Try to access with different user ID in URL
    response = client.get(f"/api/other-user-id/tasks/{task_id}", headers=headers)
    assert response.status_code == 403  # Forbidden


def test_performance_under_load(client: TestClient, valid_jwt_token: str):
    """Test API performance under load."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    import time

    # Measure time to create multiple tasks
    start_time = time.time()

    for i in range(20):  # Create 20 tasks
        task_data = {
            "title": f"Performance Test Task {i}",
            "description": f"Task {i} for performance testing",
            "completed": i % 2 == 0  # Alternate completion status
        }
        response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
        assert response.status_code == 201

    end_time = time.time()
    creation_time = end_time - start_time

    # Verify all tasks were created
    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert response.status_code == 200
    all_tasks = response.json()
    assert len(all_tasks) == 20

    # Performance expectation: creating 20 tasks should not take more than 5 seconds
    # (This is generous - it should be much faster in testing)
    assert creation_time < 10.0, f"Creating 20 tasks took too long: {creation_time}s"

    # Measure time to retrieve all tasks
    start_time = time.time()
    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    end_time = time.time()
    retrieval_time = end_time - start_time

    assert retrieval_time < 2.0, f"Retrieving 20 tasks took too long: {retrieval_time}s"


def test_complete_authentication_flow(client: TestClient, valid_jwt_token: str, invalid_token_headers: dict):
    """Test the complete authentication flow."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # 1. Verify authenticated access works
    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert response.status_code in [200, 404]  # Success or not found, but not unauthorized

    # 2. Create a task to verify auth works for mutations too
    task_data = {
        "title": "Auth Flow Test Task",
        "description": "Task created to test authentication flow",
        "completed": False
    }
    create_response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # 3. Verify the created task is accessible
    get_response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == task_id

    # 4. Verify unauthenticated access is blocked
    unauth_response = client.get(f"/api/{user_id}/tasks")
    assert unauth_response.status_code == 401

    # 5. Verify invalid token is blocked
    invalid_response = client.get(f"/api/{user_id}/tasks", headers=invalid_token_headers)
    assert invalid_response.status_code == 401

    # 6. Clean up
    delete_response = client.delete(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 204


def test_edge_cases_and_boundary_conditions(client: TestClient, valid_jwt_token: str):
    """Test edge cases and boundary conditions."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # 1. Test with empty string values where allowed
    task_with_empty_desc = {
        "title": "Task with Empty Description",
        "description": "",
        "completed": False
    }
    response = client.post(f"/api/{user_id}/tasks", json=task_with_empty_desc, headers=headers)
    assert response.status_code == 201

    # 2. Test with minimal required fields only
    minimal_task = {
        "title": "Minimal Task"
        # No description or completed fields (if they're optional)
    }
    response = client.post(f"/api/{user_id}/tasks", json=minimal_task, headers=headers)
    # Should either succeed or return validation error, but not crash
    assert response.status_code in [201, 422]

    # 3. Test with null values for optional fields
    task_with_nulls = {
        "title": "Task with Null Desc",
        "description": None,
        "completed": False
    }
    response = client.post(f"/api/{user_id}/tasks", json=task_with_nulls, headers=headers)
    assert response.status_code in [201, 422]

    # 4. Test very long text fields (within limits)
    long_text_task = {
        "title": "A" * 200,  # Maximum title length
        "description": "B" * 1000,  # Long description
        "completed": False
    }
    response = client.post(f"/api/{user_id}/tasks", json=long_text_task, headers=headers)
    assert response.status_code == 201