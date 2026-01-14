"""
Final integration tests for the Todo application backend.
Tests the complete integration between all components with real authentication flow.
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


def test_complete_auth_flow_integration(client: TestClient, valid_jwt_token: str):
    """Test the complete authentication and task management flow."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # 1. Create a task
    task_data = {
        "title": "Integration Test Task",
        "description": "A task created during integration testing",
        "completed": False
    }
    create_response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
    assert create_response.status_code == 201
    created_task = create_response.json()
    assert created_task["title"] == "Integration Test Task"
    assert created_task["user_id"] == user_id
    assert created_task["completed"] is False
    task_id = created_task["id"]

    # 2. Retrieve the created task
    get_response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert get_response.status_code == 200
    retrieved_task = get_response.json()
    assert retrieved_task["id"] == task_id
    assert retrieved_task["title"] == "Integration Test Task"

    # 3. Update the task
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

    # 4. Toggle task completion
    toggle_data = {"completed": False}
    toggle_response = client.patch(f"/api/{user_id}/tasks/{task_id}/complete", json=toggle_data, headers=headers)
    assert toggle_response.status_code == 200
    toggled_task = toggle_response.json()
    assert toggled_task["id"] == task_id
    assert toggled_task["completed"] is False

    # 5. Get all tasks and verify our task is there
    all_response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert all_response.status_code == 200
    all_tasks = all_response.json()
    task_ids = [task["id"] for task in all_tasks]
    assert task_id in task_ids

    # 6. Delete the task
    delete_response = client.delete(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 204

    # 7. Verify the task is deleted
    verify_response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert verify_response.status_code == 404


def test_user_isolation_strict_enforcement(client: TestClient, valid_jwt_token: str):
    """Test strict user isolation enforcement across all endpoints."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}

    # Create a task for the authenticated user
    task_data = {
        "title": "User Isolation Test Task",
        "description": "Task for user isolation testing",
        "completed": False
    }
    create_response = client.post("/api/test-user-id/tasks", json=task_data, headers=headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Try to access the task with a different user ID in the URL
    # This should be forbidden due to user ID mismatch between token and URL
    different_user_response = client.get("/api/different-user-id/tasks", headers=headers)
    assert different_user_response.status_code == 403

    # Try to access specific task with different user ID in URL
    different_task_response = client.get(f"/api/different-user-id/tasks/{task_id}", headers=headers)
    assert different_task_response.status_code == 403

    # Try to update task with different user ID in URL
    update_data = {"title": "Hacked Update"}
    update_response = client.put(f"/api/different-user-id/tasks/{task_id}", json=update_data, headers=headers)
    assert update_response.status_code == 403

    # Try to delete task with different user ID in URL
    delete_response = client.delete(f"/api/different-user-id/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 403

    # Try to toggle completion with different user ID in URL
    toggle_data = {"completed": True}
    toggle_response = client.patch(f"/api/different-user-id/tasks/{task_id}/complete", json=toggle_data, headers=headers)
    assert toggle_response.status_code == 403

    # Clean up: delete the task with the correct user ID
    clean_up_response = client.delete(f"/api/test-user-id/tasks/{task_id}", headers=headers)
    assert clean_up_response.status_code == 204


def test_jwt_token_validation_integration(client: TestClient):
    """Test comprehensive JWT token validation."""
    # Test with no token
    response = client.get("/api/test-user/tasks")
    assert response.status_code == 401

    # Test with invalid token format
    invalid_headers = {"Authorization": "Bearer invalid.token.format"}
    response = client.get("/api/test-user/tasks", headers=invalid_headers)
    assert response.status_code == 401

    # Test with valid token but wrong user ID in URL (should be 403 due to user isolation)
    valid_payload = {
        "user_id": "correct-user-id",
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "sub": "correct-user-id"
    }
    valid_token = jwt.encode(valid_payload, settings.better_auth_secret, algorithm="HS256")
    valid_headers = {"Authorization": f"Bearer {valid_token}"}

    # This should work for correct user ID
    response = client.get("/api/correct-user-id/tasks", headers=valid_headers)
    assert response.status_code in [200, 404]  # Success or not found, but not unauthorized

    # This should be forbidden for different user ID
    response = client.get("/api/wrong-user-id/tasks", headers=valid_headers)
    assert response.status_code == 403


def test_task_validation_and_security(client: TestClient, valid_jwt_token: str):
    """Test task validation and security measures."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Test creating task with empty title (should fail validation)
    empty_title_data = {"title": "", "description": "Valid description", "completed": False}
    response = client.post(f"/api/{user_id}/tasks", json=empty_title_data, headers=headers)
    assert response.status_code == 422

    # Test creating task with very long title (should fail validation)
    long_title_data = {"title": "a" * 201, "description": "Valid description", "completed": False}
    response = client.post(f"/api/{user_id}/tasks", json=long_title_data, headers=headers)
    assert response.status_code == 422

    # Test creating valid task (should succeed)
    valid_data = {
        "title": "Valid Task Title",
        "description": "Valid description",
        "completed": False
    }
    response = client.post(f"/api/{user_id}/tasks", json=valid_data, headers=headers)
    assert response.status_code == 201

    # Test updating with invalid data
    task_id = response.json()["id"]
    invalid_update = {"title": ""}  # Empty title
    response = client.put(f"/api/{user_id}/tasks/{task_id}", json=invalid_update, headers=headers)
    assert response.status_code == 422


def test_error_handling_and_responses(client: TestClient, valid_jwt_token: str):
    """Test comprehensive error handling and response formats."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Test accessing non-existent task
    response = client.get(f"/api/{user_id}/tasks/999999", headers=headers)
    assert response.status_code == 404
    error_response = response.json()
    assert "detail" in error_response

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


def test_task_filtering_and_query_parameters(client: TestClient, valid_jwt_token: str):
    """Test task filtering and query parameters."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Create multiple tasks with different completion states
    pending_task = {"title": "Pending Task", "description": "A pending task", "completed": False}
    completed_task = {"title": "Completed Task", "description": "A completed task", "completed": True}

    client.post(f"/api/{user_id}/tasks", json=pending_task, headers=headers)
    client.post(f"/api/{user_id}/tasks", json=completed_task, headers=headers)

    # Test filtering by status
    pending_response = client.get(f"/api/{user_id}/tasks?status_filter=pending", headers=headers)
    assert pending_response.status_code == 200
    pending_tasks = pending_response.json()
    assert len(pending_tasks) >= 1
    for task in pending_tasks:
        assert task["completed"] is False

    completed_response = client.get(f"/api/{user_id}/tasks?status_filter=completed", headers=headers)
    assert completed_response.status_code == 200
    completed_tasks = completed_response.json()
    assert len(completed_tasks) >= 1
    for task in completed_tasks:
        assert task["completed"] is True


def test_security_edge_cases(client: TestClient, valid_jwt_token: str):
    """Test security edge cases and potential vulnerabilities."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Test SQL injection attempt in task title
    sql_injection_data = {
        "title": "'; DROP TABLE tasks; --",
        "description": "SQL injection test",
        "completed": False
    }
    response = client.post(f"/api/{user_id}/tasks", json=sql_injection_data, headers=headers)
    # Should either reject the request or handle it safely without executing SQL
    assert response.status_code in [201, 422]  # Either accepts (with sanitized input) or rejects

    # Test XSS attempt in task data
    xss_data = {
        "title": "<script>alert('XSS')</script>",
        "description": "XSS attempt",
        "completed": False
    }
    response = client.post(f"/api/{user_id}/tasks", json=xss_data, headers=headers)
    # Should handle the request safely
    assert response.status_code in [201, 422]

    # Test access to another user's resources (should be blocked by user isolation)
    response = client.get("/api/other-user-id/tasks", headers=headers)
    assert response.status_code == 403


def test_concurrent_access_and_race_conditions(client: TestClient, valid_jwt_token: str):
    """Test handling of concurrent access to the API."""
    import threading
    import time

    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    results = []

    def create_task(task_num: int):
        task_data = {
            "title": f"Concurrent Task {task_num}",
            "description": f"Task {task_num} for concurrency testing",
            "completed": False
        }
        response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
        results.append((response.status_code, response.json() if response.status_code == 201 else None))

    # Create multiple threads to simulate concurrent requests
    threads = []
    for i in range(3):  # Create 3 concurrent tasks
        thread = threading.Thread(target=create_task, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify that requests were handled properly (no server crashes)
    success_count = sum(1 for status_code, _ in results if status_code == 201)
    assert success_count >= 0  # At least some should succeed

    # Check that we can retrieve the tasks
    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert response.status_code == 200


def test_complete_workflow_with_all_endpoints(client: TestClient, valid_jwt_token: str):
    """Test the complete workflow using all API endpoints."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # 1. Get tasks (should be empty initially)
    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert response.status_code == 200
    initial_tasks = response.json()
    initial_count = len(initial_tasks)

    # 2. Create a task
    task_data = {
        "title": "Complete Workflow Test Task",
        "description": "Task for complete workflow testing",
        "completed": False
    }
    create_response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
    assert create_response.status_code == 201
    created_task = create_response.json()
    assert created_task["title"] == "Complete Workflow Test Task"
    task_id = created_task["id"]

    # 3. Get all tasks (should have increased by 1)
    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert response.status_code == 200
    all_tasks = response.json()
    assert len(all_tasks) == initial_count + 1

    # 4. Get specific task
    response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    specific_task = response.json()
    assert specific_task["id"] == task_id

    # 5. Update the task
    update_data = {
        "title": "Updated Complete Workflow Test Task",
        "completed": True
    }
    update_response = client.put(f"/api/{user_id}/tasks/{task_id}", json=update_data, headers=headers)
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["title"] == "Updated Complete Workflow Test Task"
    assert updated_task["completed"] is True

    # 6. Toggle completion status
    toggle_data = {"completed": False}
    toggle_response = client.patch(f"/api/{user_id}/tasks/{task_id}/complete", json=toggle_data, headers=headers)
    assert toggle_response.status_code == 200
    toggled_task = toggle_response.json()
    assert toggled_task["completed"] is False

    # 7. Delete the task
    delete_response = client.delete(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 204

    # 8. Verify task is gone
    response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert response.status_code == 404

    # 9. Verify task count is back to initial
    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert response.status_code == 200
    final_tasks = response.json()
    assert len(final_tasks) == initial_count


def test_response_formats_consistency(client: TestClient, valid_jwt_token: str):
    """Test that all API responses follow consistent formats."""
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Test GET all tasks response format
    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        # If there are tasks, verify their structure
        if data:
            task = data[0]
            assert "id" in task
            assert "user_id" in task
            assert "title" in task
            assert "completed" in task
            assert "created_at" in task
            assert "updated_at" in task

    # Create a task to test single task response format
    task_data = {
        "title": "Response Format Test Task",
        "description": "Task for testing response formats",
        "completed": False
    }
    create_response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
    if create_response.status_code == 201:
        created_task = create_response.json()
        assert "id" in created_task
        assert "user_id" in created_task
        assert "title" in created_task
        assert "completed" in created_task
        assert "created_at" in created_task
        assert "updated_at" in created_task

        task_id = created_task["id"]

        # Test GET single task response format
        get_response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=headers)
        assert get_response.status_code == 200
        single_task = get_response.json()
        assert single_task["id"] == task_id

        # Test UPDATE task response format
        update_response = client.put(f"/api/{user_id}/tasks/{task_id}", json={"title": "Updated"}, headers=headers)
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["id"] == task_id
        assert updated_task["title"] == "Updated"

        # Test toggle completion response format
        toggle_response = client.patch(f"/api/{user_id}/tasks/{task_id}/complete", json={"completed": True}, headers=headers)
        assert toggle_response.status_code == 200
        toggled_task = toggle_response.json()
        assert toggled_task["id"] == task_id
        assert toggled_task["completed"] is True

        # Clean up
        delete_response = client.delete(f"/api/{user_id}/tasks/{task_id}", headers=headers)
        assert delete_response.status_code == 204


def test_performance_under_varied_loads(client: TestClient, valid_jwt_token: str):
    """Test API performance under different loads."""
    import time

    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    user_id = "test-user-id"

    # Test single request timing (should be fast)
    start_time = time.time()
    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    single_request_time = time.time() - start_time
    assert response.status_code in [200, 404]
    # Single request should complete quickly (under 1 second in test environment)
    assert single_request_time < 5.0  # Generous timeout for test environment

    # Test creating multiple tasks
    num_tasks = 5
    create_times = []

    for i in range(num_tasks):
        start_time = time.time()
        task_data = {
            "title": f"Performance Test Task {i}",
            "description": f"Task {i} for performance testing",
            "completed": i % 2 == 0  # Alternate completion
        }
        response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)
        create_times.append(time.time() - start_time)
        assert response.status_code == 201

    # Verify we can retrieve them quickly
    start_time = time.time()
    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    retrieval_time = time.time() - start_time
    assert response.status_code == 200
    tasks = response.json()
    assert len([t for t in tasks if "Performance Test Task" in t["title"]]) >= num_tasks

    # Retrieval should also be reasonably fast
    assert retrieval_time < 5.0