import requests
import json
from datetime import datetime

# Set the base URL for the API
BASE_URL = "http://127.0.0.1:8003"

def test_task_creation_minimal():
    print("Testing minimal task creation...")

    # Register a new user
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"min_test_{timestamp}@example.com"

    print(f"Registering user with email: {test_email}")

    # Register
    reg_data = {
        "name": "Min Test User",
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

        # Try the absolute minimal task creation
        print("Creating minimal task (just title)...")
        task_data = {
            "title": "Minimal Test Task"
        }

        task_resp = requests.post(f"{BASE_URL}/api/tasks/", json=task_data, headers=headers)
        print(f"Task creation response: {task_resp.status_code}")

        # Try to get more detailed information about the error
        if task_resp.status_code != 200:
            print(f"Task creation failed: {task_resp.text}")

            # Try with description only
            print("Trying with title and description...")
            task_data2 = {
                "title": "Test Task 2",
                "description": "Test description"
            }
            task_resp2 = requests.post(f"{BASE_URL}/api/tasks/", json=task_data2, headers=headers)
            print(f"Task creation response 2: {task_resp2.status_code}")
            if task_resp2.status_code != 200:
                print(f"Task creation failed again: {task_resp2.text}")
        else:
            print(f"Task created successfully: {task_resp.json()}")

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_task_creation_minimal()