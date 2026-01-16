import requests
import json
import time

# Test credentials
TEST_USER = {
    "name": "pqr",
    "email": "pqr@gmail.com",
    "password": "PQRpqr@1!"
}

BASE_URL = "http://localhost:8000"

def test_registration():
    print("Testing Registration API...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=TEST_USER)
        print(f"Registration Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Registration successful!")
            print(f"Access Token: {result['access_token'][:20]}...")
            return result['access_token']
        else:
            print(f"Registration failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during registration: {e}")
        return None

def test_login():
    print("\nTesting Login API...")
    try:
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Login Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Login successful!")
            print(f"Access Token: {result['access_token'][:20]}...")
            return result['access_token']
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def test_tasks_api(token):
    print("\nTesting Tasks API with JWT Token...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Test creating a task
    print("\nCreating a task...")
    task_data = {
        "title": "Test task from API test",
        "description": "This is a test task created via the API"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/tasks/", json=task_data, headers=headers)
        print(f"Create Task Status: {response.status_code}")
        if response.status_code == 200:
            task = response.json()
            print(f"Task created successfully with ID: {task['id']}")
            task_id = task['id']

            # Test getting all tasks
            print("\nGetting all tasks...")
            response = requests.get(f"{BASE_URL}/api/tasks/", headers=headers)
            print(f"Get Tasks Status: {response.status_code}")
            if response.status_code == 200:
                tasks = response.json()
                print(f"Found {len(tasks)} tasks")

                # Test updating the task
                print(f"\nUpdating task {task_id}...")
                update_data = {
                    "title": "Updated test task",
                    "description": "This is an updated test task"
                }
                response = requests.put(f"{BASE_URL}/api/tasks/{task_id}", json=update_data, headers=headers)
                print(f"Update Task Status: {response.status_code}")
                if response.status_code == 200:
                    print("Task updated successfully!")

                    # Test toggling completion
                    print(f"\nToggling task completion for {task_id}...")
                    completion_data = {"completed": True}
                    response = requests.patch(f"{BASE_URL}/api/tasks/{task_id}/complete", json=completion_data, headers=headers)
                    print(f"Toggle Completion Status: {response.status_code}")
                    if response.status_code == 200:
                        print("Task completion toggled successfully!")

                        # Test getting specific task
                        print(f"\nGetting specific task {task_id}...")
                        response = requests.get(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
                        print(f"Get Specific Task Status: {response.status_code}")
                        if response.status_code == 200:
                            specific_task = response.json()
                            print(f"Retrieved task: {specific_task['title']}")

                            # Test deleting the task
                            print(f"\nDeleting task {task_id}...")
                            response = requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
                            print(f"Delete Task Status: {response.status_code}")
                            if response.status_code == 200:
                                print("Task deleted successfully!")
                                return True
                            else:
                                print(f"Failed to delete task: {response.text}")
                        else:
                            print(f"Failed to get specific task: {response.text}")
                    else:
                        print(f"Failed to toggle task completion: {response.text}")
                else:
                    print(f"Failed to update task: {response.text}")
            else:
                print(f"Failed to get tasks: {response.text}")
        else:
            print(f"Failed to create task: {response.text}")
            return False
    except Exception as e:
        print(f"Error during tasks API test: {e}")
        return False

def main():
    print("Starting API tests...")

    # First try to register (might fail if user already exists)
    token = test_registration()

    # If registration fails due to user already existing, try login
    if not token:
        print("\nTrying login instead (user might already exist)...")
        token = test_login()

    if token:
        # Test tasks API with the obtained token
        success = test_tasks_api(token)
        if success:
            print("\nSUCCESS: All API tests passed!")
        else:
            print("\nERROR: Some API tests failed!")
    else:
        print("\nERROR: Could not obtain token for API tests!")

if __name__ == "__main__":
    main()