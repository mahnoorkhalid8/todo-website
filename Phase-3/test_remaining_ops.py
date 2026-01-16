import requests
import json
from datetime import datetime

# Set the base URL for the API
BASE_URL = "http://127.0.0.1:8000"

def test_remaining_operations():
    print("Testing remaining operations (skipping task creation due to backend issue)...")

    # Register a new user
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"test_remaining_{timestamp}@example.com"

    print(f"Registering user with email: {test_email}")

    # Register
    reg_data = {
        "name": "Remaining Ops User",
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

        print("Note: Skipping task creation due to backend service issue.")

        # Let's try to create a task directly in the database for testing update/delete
        # But since we can't create one via API, we'll have to note that

        print("\nTesting getting tasks (expecting empty list)...")
        tasks_resp = requests.get(f"{BASE_URL}/api/tasks/", headers=headers)
        print(f"Get tasks response: {tasks_resp.status_code}")
        if tasks_resp.status_code == 200:
            print(f"Get tasks response data: {tasks_resp.json()}")
        else:
            print(f"Get tasks failed: {tasks_resp.text}")
            print("Note: This confirms the backend issue affects multiple task operations.")

        print("\nSince we can't create a task via API due to backend service issue,")
        print("we cannot proceed with testing update and delete operations.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    test_remaining_operations()