import requests
import json
import time
import subprocess
import os
from datetime import datetime

# Set the base URL for the API
BASE_URL = "http://127.0.0.1:8000"

def test_api_endpoints():
    print("Testing API endpoints...")

    # Test health check
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return

    # Generate unique email for this test run
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"test_{timestamp}@example.com"

    # Test registration
    print("\n1. Testing user registration...")
    registration_data = {
        "name": "Test User",
        "email": test_email,
        "password": "Password123!"  # Must contain uppercase letter and special character
    }

    try:
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json=registration_data)
        print(f"Registration response: {reg_response.status_code}")
        print(f"Registration data: {reg_response.json()}")

        if reg_response.status_code != 200:
            print(f"Registration failed: {reg_response.text}")
            return

        # Extract token
        token_data = reg_response.json()
        access_token = token_data.get("access_token")
        print(f"Access token received: {access_token[:20]}..." if access_token else "No token received")

    except Exception as e:
        print(f"Registration failed: {e}")
        return

    # Test login
    print("\n2. Testing user login...")
    login_data = {
        "email": test_email,
        "password": "Password123!"
    }

    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Login response: {login_response.status_code}")
        print(f"Login data: {login_response.json()}")

        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return

        # Extract token from login
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        print(f"Access token from login: {access_token[:20]}..." if access_token else "No token received")

    except Exception as e:
        print(f"Login failed: {e}")
        return

    # Use the token for authenticated requests
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Test task creation
    print("\n3. Testing task creation...")
    task_data = {
        "title": "Test Task",
        "description": "This is a test task"
        # Note: due_date is optional, so we'll omit it for this test
    }

    try:
        task_response = requests.post(f"{BASE_URL}/api/tasks/", json=task_data, headers=headers)
        print(f"Task creation response: {task_response.status_code}")
        print(f"Task creation data: {task_response.json()}")

        if task_response.status_code != 200:
            print(f"Task creation failed: {task_response.text}")
            return

        task_id = task_response.json().get("id")
        print(f"Created task with ID: {task_id}")

    except Exception as e:
        print(f"Task creation failed: {e}")
        return

    # Test getting tasks
    print("\n4. Testing getting tasks...")
    try:
        get_tasks_response = requests.get(f"{BASE_URL}/api/tasks/", headers=headers)
        print(f"Get tasks response: {get_tasks_response.status_code}")
        print(f"Tasks data: {get_tasks_response.json()}")

        if get_tasks_response.status_code != 200:
            print(f"Getting tasks failed: {get_tasks_response.text}")

    except Exception as e:
        print(f"Getting tasks failed: {e}")

    # Test task update
    print("\n5. Testing task update...")
    if task_id:
        update_data = {
            "title": "Updated Test Task",
            "description": "This is an updated test task"
        }

        try:
            update_response = requests.put(f"{BASE_URL}/api/tasks/{task_id}", json=update_data, headers=headers)
            print(f"Task update response: {update_response.status_code}")
            print(f"Task update data: {update_response.json()}")

            if update_response.status_code != 200:
                print(f"Task update failed: {update_response.text}")

        except Exception as e:
            print(f"Task update failed: {e}")

    # Test task completion toggle
    print("\n6. Testing task completion toggle...")
    if task_id:
        completion_data = {
            "completed": True
        }

        try:
            completion_response = requests.patch(f"{BASE_URL}/api/tasks/{task_id}/complete", json=completion_data, headers=headers)
            print(f"Task completion response: {completion_response.status_code}")
            print(f"Task completion data: {completion_response.json()}")

            if completion_response.status_code != 200:
                print(f"Task completion failed: {completion_response.text}")

        except Exception as e:
            print(f"Task completion failed: {e}")

    # Test task deletion
    print("\n7. Testing task deletion...")
    if task_id:
        try:
            delete_response = requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
            print(f"Task deletion response: {delete_response.status_code}")
            print(f"Task deletion data: {delete_response.json()}")

            if delete_response.status_code != 200:
                print(f"Task deletion failed: {delete_response.text}")
            else:
                print("Task deleted successfully!")

        except Exception as e:
            print(f"Task deletion failed: {e}")

if __name__ == "__main__":
    test_api_endpoints()