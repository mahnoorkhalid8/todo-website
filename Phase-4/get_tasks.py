import requests
import json
from datetime import datetime

# Set the base URL for the API
BASE_URL = "http://127.0.0.1:8000"

def test_get_tasks():
    print("Testing getting tasks...")

    # Register a new user
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"get_tasks_{timestamp}@example.com"

    print(f"Registering user with email: {test_email}")

    # Register
    reg_data = {
        "name": "Get Tasks User",
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

        # Try to get tasks (should return empty list)
        print("Getting tasks...")
        tasks_resp = requests.get(f"{BASE_URL}/api/tasks/", headers=headers)
        print(f"Get tasks response: {tasks_resp.status_code}")
        print(f"Get tasks response text: {tasks_resp.text}")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    test_get_tasks()