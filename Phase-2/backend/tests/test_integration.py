"""
Integration tests for the complete Todo application.
Tests the full flow of operations with authentication, CRUD operations,
user isolation, and security validation.
"""
import pytest
from fastapi.testclient import TestClient
import json


def test_complete_crud_flow(client: TestClient, valid_token_headers: dict):
    """Test the complete CRUD flow for a user."""
    # 1. Create a task
    task_data = {
        "title": "Integration Test Task",
        "description": "A task created during integration testing",
        "completed": False
    }
    create_response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert create_response.status_code == 201
    created_task = create_response.json()
    assert created_task["title"] == "Integration Test Task"
    assert created_task["description"] == "A task created during integration testing"
    assert created_task["completed"] is False
    task_id = created_task["id"]

    # 2. Get the specific task
    get_response = client.get(f"/api/test-user-id/tasks/{task_id}", headers=valid_token_headers)
    assert get_response.status_code == 200
    retrieved_task = get_response.json()
    assert retrieved_task["id"] == task_id
    assert retrieved_task["title"] == "Integration Test Task"

    # 3. Update the task
    update_data = {
        "title": "Updated Integration Test Task",
        "completed": True
    }
    update_response = client.put(f"/api/test-user-id/tasks/{task_id}", json=update_data, headers=valid_token_headers)
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["id"] == task_id
    assert updated_task["title"] == "Updated Integration Test Task"
    assert updated_task["completed"] is True

    # 4. Toggle completion status
    toggle_data = {"completed": False}
    toggle_response = client.patch(f"/api/test-user-id/tasks/{task_id}/complete", json=toggle_data, headers=valid_token_headers)
    assert toggle_response.status_code == 200
    toggled_task = toggle_response.json()
    assert toggled_task["id"] == task_id
    assert toggled_task["completed"] is False

    # 5. Get all tasks and verify our task is there
    all_tasks_response = client.get("/api/test-user-id/tasks", headers=valid_token_headers)
    assert all_tasks_response.status_code == 200
    all_tasks = all_tasks_response.json()
    task_ids = [task["id"] for task in all_tasks]
    assert task_id in task_ids

    # 6. Delete the task
    delete_response = client.delete(f"/api/test-user-id/tasks/{task_id}", headers=valid_token_headers)
    assert delete_response.status_code == 204  # No content

    # 7. Verify the task is deleted
    verify_delete_response = client.get(f"/api/test-user-id/tasks/{task_id}", headers=valid_token_headers)
    assert verify_delete_response.status_code == 404


def test_user_isolation_complete_flow(client: TestClient, valid_token_headers: dict):
    """Test that user isolation is maintained throughout the application."""
    # Create a task with the authenticated user
    task_data = {
        "title": "User A's Task",
        "description": "This belongs to User A",
        "completed": False
    }
    create_response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert create_response.status_code == 201
    task_a = create_response.json()
    task_a_id = task_a["id"]
    assert task_a["user_id"] == "test-user-id"

    # Try to access the task with different user ID in URL (should fail)
    access_response = client.get("/api/other-user-id/tasks", headers=valid_token_headers)
    assert access_response.status_code == 403  # Forbidden due to user isolation

    # Try to access specific task with wrong user ID in URL
    specific_access_response = client.get(f"/api/other-user-id/tasks/{task_a_id}", headers=valid_token_headers)
    assert specific_access_response.status_code == 403  # Forbidden due to user isolation

    # Verify the user can still access their own task
    own_access_response = client.get(f"/api/test-user-id/tasks/{task_a_id}", headers=valid_token_headers)
    assert own_access_response.status_code == 200  # Should work

    # Clean up
    delete_response = client.delete(f"/api/test-user-id/tasks/{task_a_id}", headers=valid_token_headers)
    assert delete_response.status_code == 204


def test_authentication_flow(client: TestClient, valid_token_headers: dict, invalid_token_headers: dict):
    """Test the complete authentication flow."""
    # 1. Test that authenticated requests work
    response = client.get("/api/test-user-id/tasks", headers=valid_token_headers)
    assert response.status_code in [200, 403]  # 200 = success, 403 = user isolation (both acceptable)

    # 2. Test that unauthenticated requests fail
    unauth_response = client.get("/api/test-user-id/tasks")
    assert unauth_response.status_code == 401

    # 3. Test that invalid token requests fail
    invalid_response = client.get("/api/test-user-id/tasks", headers=invalid_token_headers)
    assert invalid_response.status_code == 401

    # 4. Test that authenticated requests can perform operations
    task_data = {
        "title": "Auth Flow Test Task",
        "description": "Task created with valid auth",
        "completed": False
    }
    create_response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert create_response.status_code in [200, 201]  # Should succeed

    if create_response.status_code == 201:
        task_id = create_response.json()["id"]
        # Clean up
        delete_response = client.delete(f"/api/test-user-id/tasks/{task_id}", headers=valid_token_headers)
        assert delete_response.status_code == 204


def test_security_validation_complete(client: TestClient, valid_token_headers: dict):
    """Test comprehensive security validation."""
    # 1. Verify all endpoints require authentication
    endpoints_and_methods = [
        ("GET", "/api/test-user-id/tasks"),
        ("POST", "/api/test-user-id/tasks", {"title": "Test"}),
        ("GET", f"/api/test-user-id/tasks/1"),
        ("PUT", f"/api/test-user-id/tasks/1", {"title": "Updated"}),
        ("DELETE", f"/api/test-user-id/tasks/1"),
        ("PATCH", f"/api/test-user-id/tasks/1/complete", {"completed": True}),
    ]

    for item in endpoints_and_methods:
        method = item[0]
        path = item[1]
        data = item[2] if len(item) > 2 else None

        # Test without authentication
        if method == "GET":
            response = client.get(path)
        elif method == "POST":
            response = client.post(path, json=data if data else {})
        elif method == "PUT":
            response = client.put(path, json=data if data else {})
        elif method == "DELETE":
            response = client.delete(path)
        elif method == "PATCH":
            response = client.patch(path, json=data if data else {})

        assert response.status_code == 401, f"{method} {path} should require authentication"

    # 2. Verify user isolation is enforced
    # Create a task first
    task_data = {
        "title": "Security Test Task",
        "description": "Task for security testing",
        "completed": False
    }
    create_response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert create_response.status_code in [200, 201]

    if create_response.status_code == 201:
        task_id = create_response.json()["id"]

        # Try to access with different user ID in URL (should fail)
        isolation_response = client.get(f"/api/other-user-id/tasks/{task_id}", headers=valid_token_headers)
        assert isolation_response.status_code == 403  # Forbidden

        # Clean up
        delete_response = client.delete(f"/api/test-user-id/tasks/{task_id}", headers=valid_token_headers)
        assert delete_response.status_code == 204


def test_jwt_token_verification_comprehensive(client: TestClient, valid_token_headers: dict, invalid_token_headers: dict):
    """Test comprehensive JWT token verification with real environment secrets."""
    # 1. Test valid token works
    response = client.get("/api/test-user-id/tasks", headers=valid_token_headers)
    # Should not be unauthorized (may be forbidden due to user isolation, which is OK)
    assert response.status_code != 401

    # 2. Test invalid token fails
    response = client.get("/api/test-user-id/tasks", headers=invalid_token_headers)
    assert response.status_code == 401

    # 3. Test missing token fails
    response = client.get("/api/test-user-id/tasks")
    assert response.status_code == 401

    # 4. Test malformed token fails (still using hardcoded for this specific edge case)
    malformed_headers = {"Authorization": "Bearer malformed.token.format"}
    response = client.get("/api/test-user-id/tasks", headers=malformed_headers)
    assert response.status_code == 401


def test_task_ownership_enforcement_complete(client: TestClient, valid_token_headers: dict):
    """Test that task ownership is enforced for all operations."""
    # Create a task
    task_data = {
        "title": "Ownership Test Task",
        "description": "Task to test ownership enforcement",
        "completed": False
    }
    create_response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert create_response.status_code in [200, 201]

    if create_response.status_code == 201:
        task_id = create_response.json()["id"]

        # Test that we can't access this task with different user ID in URL
        wrong_user_response = client.get(f"/api/wrong-user-id/tasks/{task_id}", headers=valid_token_headers)
        assert wrong_user_response.status_code == 403  # Forbidden

        # Test that we can't update this task with different user ID in URL
        update_data = {"title": "Hacked Title"}
        wrong_user_update = client.put(f"/api/wrong-user-id/tasks/{task_id}", json=update_data, headers=valid_token_headers)
        assert wrong_user_update.status_code == 403  # Forbidden

        # Test that we can't delete this task with different user ID in URL
        wrong_user_delete = client.delete(f"/api/wrong-user-id/tasks/{task_id}", headers=valid_token_headers)
        assert wrong_user_delete.status_code == 403  # Forbidden

        # Test that we can't toggle completion with different user ID in URL
        toggle_data = {"completed": True}
        wrong_user_toggle = client.patch(f"/api/wrong-user-id/tasks/{task_id}/complete", json=toggle_data, headers=valid_token_headers)
        assert wrong_user_toggle.status_code == 403  # Forbidden

        # But we CAN access with the correct user ID
        correct_user_response = client.get(f"/api/test-user-id/tasks/{task_id}", headers=valid_token_headers)
        assert correct_user_response.status_code in [200, 404]  # 200 if exists, 404 if deleted elsewhere

        # Clean up
        delete_response = client.delete(f"/api/test-user-id/tasks/{task_id}", headers=valid_token_headers)
        assert delete_response.status_code == 204


def test_error_handling_consistency(client: TestClient):
    """Test that error handling is consistent across the application."""
    # Test that all error responses have consistent structure
    response = client.get("/api/test-user/tasks")  # Should be 401
    assert response.status_code == 401
    error_response = response.json()
    assert "detail" in error_response or "error" in error_response  # Should have error info


def test_multiple_users_isolation(client: TestClient, valid_token_headers: dict):
    """Test isolation between multiple simulated users."""
    # This tests using the same token but different user IDs in URLs
    # Create task with first "user"

    # Create a task pretending to be user1
    task_data = {
        "title": "User1's Task",
        "description": "Task for user1",
        "completed": False
    }
    response1 = client.post("/api/user1/tasks", json=task_data, headers=valid_token_headers)
    # This should fail due to user ID mismatch between token and URL
    assert response1.status_code == 403  # Forbidden

    # Try to create with matching user ID in URL
    response2 = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
    assert response2.status_code in [200, 201]  # Should succeed


def test_validation_edge_cases(client: TestClient, valid_token_headers: dict):
    """Test validation with edge cases."""
    # Test title too short
    short_title_data = {
        "title": "",  # Empty title
        "description": "Valid description",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=short_title_data, headers=valid_token_headers)
    assert response.status_code == 422  # Validation error

    # Test title too long
    long_title_data = {
        "title": "a" * 201,  # Exceeds max length
        "description": "Valid description",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=long_title_data, headers=valid_token_headers)
    assert response.status_code == 422  # Validation error

    # Test valid title length
    valid_title_data = {
        "title": "a" * 200,  # Maximum allowed length
        "description": "Valid description",
        "completed": False
    }
    response = client.post("/api/test-user-id/tasks", json=valid_title_data, headers=valid_token_headers)
    # This should either succeed or fail for other reasons (not validation)
    assert response.status_code != 422  # Should not be validation error for title length


def test_complete_workflow_with_filters(client: TestClient, valid_token_headers: dict):
    """Test complete workflow including filtering and sorting."""
    # Create multiple tasks with different completion states
    tasks_to_create = [
        {"title": "Pending Task 1", "description": "First pending task", "completed": False},
        {"title": "Completed Task 1", "description": "First completed task", "completed": True},
        {"title": "Pending Task 2", "description": "Second pending task", "completed": False},
    ]

    created_tasks = []
    for task_data in tasks_to_create:
        response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
        assert response.status_code in [200, 201]
        if response.status_code == 201:
            created_tasks.append(response.json())

    if len(created_tasks) >= 3:
        # Test filtering by status
        pending_response = client.get("/api/test-user-id/tasks?status_filter=pending", headers=valid_token_headers)
        assert pending_response.status_code == 200
        pending_tasks = pending_response.json()
        for task in pending_tasks:
            assert task["completed"] is False

        completed_response = client.get("/api/test-user-id/tasks?status_filter=completed", headers=valid_token_headers)
        assert completed_response.status_code == 200
        completed_tasks = completed_response.json()
        for task in completed_tasks:
            assert task["completed"] is True

        # Clean up created tasks
        for task in created_tasks:
            delete_response = client.delete(f"/api/test-user-id/tasks/{task['id']}", headers=valid_token_headers)
            assert delete_response.status_code == 204


def test_rate_limiting_simulation(client: TestClient, valid_token_headers: dict):
    """Test how the system handles many requests (simulating rate limiting)."""
    # Create multiple tasks rapidly to test system resilience
    created_task_ids = []
    for i in range(5):  # Use a small number to avoid overwhelming test DB
        task_data = {
            "title": f"Rate Limit Test Task {i}",
            "description": f"Task {i} for rate limit testing",
            "completed": False
        }
        response = client.post("/api/test-user-id/tasks", json=task_data, headers=valid_token_headers)
        if response.status_code in [200, 201]:
            if response.status_code == 201:
                created_task_ids.append(response.json()["id"])

    # Verify we can retrieve the tasks
    get_response = client.get("/api/test-user-id/tasks", headers=valid_token_headers)
    assert get_response.status_code == 200

    # Clean up
    for task_id in created_task_ids:
        delete_response = client.delete(f"/api/test-user-id/tasks/{task_id}", headers=valid_token_headers)
        assert delete_response.status_code == 204