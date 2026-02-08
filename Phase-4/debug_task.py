import requests
import json
from datetime import datetime

# Set the base URL for the API
BASE_URL = "http://127.0.0.1:8000"

def test_task_creation_debug():
    print("Debug: Testing task creation...")

    # Register a new user
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"debug_{timestamp}@example.com"

    print(f"Registering user with email: {test_email}")

    # Register
    reg_data = {
        "name": "Debug User",
        "email": test_email,
        "password": "Password123!"
    }

    try:
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json=reg_data)
        print(f"Registration: {reg_resp.status_code}")
        if reg_resp.status_code != 200:
            print(f"Registration failed: {reg_resp.text}")
            return

        token_data = reg_resp.json()
        access_token = token_data.get("access_token")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Test the simplest possible task creation
        print("Creating simple task...")
        task_data = {
            "title": "Simple Test Task"
        }

        task_resp = requests.post(f"{BASE_URL}/api/tasks/", json=task_data, headers=headers)
        print(f"Task creation response: {task_resp.status_code}")
        print(f"Task creation response text: {task_resp.text}")

        if task_resp.status_code == 200:
            task_result = task_resp.json()
            print(f"Task created successfully: {task_result}")
        else:
            print("Task creation failed")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    test_task_creation_debug()