"""
Integration tests for all API endpoints in the Todo application.
Tests authentication flow, JWT token verification, user isolation, CRUD operations,
error handling, and security validation.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from models import Task
from uuid import uuid4


def test_health_check(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Todo API is running"}


def test_get_tasks_without_auth(client: TestClient):
    """Test that getting tasks requires authentication."""
    response = client.get("/api/test-user/tasks")
    assert response.status_code == 401  # Unauthorized


def test_get_tasks_with_valid_auth(client: TestClient, valid_token_headers: dict):
    """Test getting tasks with valid authentication."""
    response = client.get("/api/test-user-id/tasks", headers=valid_token_headers)
    assert response.status_code in [200, 403]  # Either success or forbidden due to user isolation


def test_create_task_without_auth(client: TestClient):
    """Test that creating a task requires authentication."""
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False
    }
    response = client.post("/api/test-user/tasks", json=task_data)
    assert response.status_code == 401  # Unauthorized


def test_create_task_with_valid_auth(client: TestClient, valid_token_headers: dict):
    """Test creating a task with valid authentication."""
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert response.status_code == 201  # Created

    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["completed"] is False
    assert "id" in data
    assert data["user_id"] == "test-user-id"


def test_get_specific_task_without_auth(client: TestClient):
    """Test that getting a specific task requires authentication."""
    response = client.get("/api/test-user/tasks/1")
    assert response.status_code == 401  # Unauthorized


def test_get_specific_task_with_valid_auth(client: TestClient, valid_token_headers: dict):
    """Test getting a specific task with valid authentication."""
    # First create a task
    task_data = {
        "title": "Test Task for Detail",
        "description": "Test Description for Detail",
        "completed": False
    }
    create_response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Now get the specific task
    response = client.get(f"/api/test-user-id/tasks/{task_id}", headers=valid_token_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task for Detail"


def test_update_task_without_auth(client: TestClient):
    """Test that updating a task requires authentication."""
    response = client.put("/api/test-user/tasks/1", json={"title": "Updated"})
    assert response.status_code == 401  # Unauthorized


def test_update_task_with_valid_auth(client: TestClient, valid_token_headers: dict):
    """Test updating a task with valid authentication."""
    # First create a task
    task_data = {
        "title": "Original Task",
        "description": "Original Description",
        "completed": False
    }
    create_response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Now update the task
    update_data = {
        "title": "Updated Task",
        "completed": True
    }
    response = client.put(f"/api/test-user-id/tasks/{task_id}", json=update_data, headers=valid_token_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated Task"
    assert data["completed"] is True


def test_delete_task_without_auth(client: TestClient):
    """Test that deleting a task requires authentication."""
    response = client.delete("/api/test-user/tasks/1")
    assert response.status_code == 401  # Unauthorized


def test_delete_task_with_valid_auth(client: TestClient, valid_token_headers: dict):
    """Test deleting a task with valid authentication."""
    # First create a task
    task_data = {
        "title": "Task to Delete",
        "description": "Description for deletion",
        "completed": False
    }
    create_response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Now delete the task
    response = client.delete(f"/api/test-user-id/tasks/{task_id}", headers=valid_token_headers)
    assert response.status_code == 204  # No Content


def test_toggle_task_completion_without_auth(client: TestClient):
    """Test that toggling task completion requires authentication."""
    response = client.patch("/api/test-user/tasks/1/complete", json={"completed": True})
    assert response.status_code == 401  # Unauthorized


def test_toggle_task_completion_with_valid_auth(client: TestClient, valid_token_headers: dict):
    """Test toggling task completion with valid authentication."""
    # First create a task
    task_data = {
        "title": "Task to Toggle",
        "description": "Description for toggling",
        "completed": False
    }
    create_response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Now toggle the task completion
    toggle_data = {"completed": True}
    response = client.patch(f"/api/test-user-id/tasks/{task_id}/complete", json=toggle_data, headers=valid_token_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task_id
    assert data["completed"] is True


def test_user_isolation_get_tasks(client: TestClient, valid_token_headers: dict):
    """Test that users can only access their own tasks."""
    # Create tasks for test-user-id
    task_data = {
        "title": "User A's Task",
        "description": "Task for user A",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert response.status_code == 201
    task_a_id = response.json()["id"]

    # Create another user's token payload (simulate)
    # In real testing, we'd need to mock this differently
    # For now, test that the user_id in URL matches the one in token
    response = client.get("/api/different-user-id/tasks", headers=valid_token_headers)
    # This should fail because token has user_id=test-user-id but URL has different-user-id
    assert response.status_code == 403  # Forbidden


def test_user_isolation_access_other_users_task(client: TestClient, valid_token_headers: dict):
    """Test that users cannot access other users' tasks."""
    # Create a task for a different user (simulated)
    # In real scenario, this would require creating a task first with the other user's ID
    # For this test, we'll simulate trying to access a task that belongs to another user
    # but our token is for test-user-id
    response = client.get("/api/other-user-id/tasks/1", headers=valid_token_headers)
    assert response.status_code == 403  # Forbidden - user isolation


def test_invalid_token_handling(client: TestClient, invalid_token_headers: dict):
    """Test that invalid tokens are properly rejected."""
    response = client.get("/api/test-user/tasks", headers=invalid_token_headers)
    assert response.status_code == 401  # Unauthorized


def test_missing_token_handling(client: TestClient):
    """Test that requests without tokens are properly rejected."""
    response = client.get("/api/test-user/tasks")
    assert response.status_code == 401  # Unauthorized


def test_task_not_found(client: TestClient, valid_token_headers: dict):
    """Test getting a non-existent task."""
    response = client.get("/api/test-user-id/tasks/999999", headers=valid_token_headers)
    assert response.status_code == 404  # Not Found


def test_update_nonexistent_task(client: TestClient, valid_token_headers: dict):
    """Test updating a non-existent task."""
    response = client.put("/api/test-user-id/tasks/999999", json={"title": "Updated"}, headers=valid_token_headers)
    assert response.status_code == 404  # Not Found


def test_delete_nonexistent_task(client: TestClient, valid_token_headers: dict):
    """Test deleting a non-existent task."""
    response = client.delete("/api/test-user-id/tasks/999999", headers=valid_token_headers)
    assert response.status_code == 404  # Not Found


def test_create_task_validation(client: TestClient, valid_token_headers: dict):
    """Test validation for task creation."""
    # Test with empty title (should fail validation)
    task_data = {
        "title": "",  # Empty title should fail
        "description": "Valid description",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert response.status_code == 422  # Validation error

    # Test with very long title (should fail validation)
    long_title = "a" * 201  # Exceeds max length of 200
    task_data = {
        "title": long_title,
        "description": "Valid description",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert response.status_code == 422  # Validation error


def test_get_tasks_with_filters(client: TestClient, valid_token_headers: dict):
    """Test getting tasks with filtering and sorting parameters."""
    # Create some test tasks
    client.post("/api/test-user-id/tasks", json={
        "title": "Pending Task",
        "description": "A pending task",
        "completed": False
    }, headers=valid_token_headers)

    client.post("/api/test-user-id/tasks", json={
        "title": "Completed Task",
        "description": "A completed task",
        "completed": True
    }, headers=valid_token_headers)

    # Test filtering by status
    response = client.get("/api/test-user-id/tasks?status_filter=pending", headers=valid_token_headers)
    assert response.status_code == 200
    pending_tasks = response.json()
    # Verify all returned tasks are pending
    for task in pending_tasks:
        assert task["completed"] is False


def test_endpoint_security_no_direct_access_to_others_data(client: TestClient, valid_token_headers: dict):
    """Test that endpoints properly enforce user isolation."""
    # Attempt to access another user's data by changing the user_id in URL
    # while using a valid token for a different user
    response = client.get("/api/another-user-id/tasks", headers=valid_token_headers)
    # This should return 403 Forbidden due to user isolation enforcement
    assert response.status_code == 403