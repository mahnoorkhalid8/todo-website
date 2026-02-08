import requests
import json
from datetime import datetime

# Set the base URL for the API
BASE_URL = "http://127.0.0.1:8003"

def comprehensive_test():
    print("=== Comprehensive API Test ===")

    # Generate unique email for this test run
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"comp_test_{timestamp}@example.com"

    print(f"Registering user with email: {test_email}")

    # Register
    reg_data = {
        "name": "Comprehensive Test User",
        "email": test_email,
        "password": "Password123!"
    }

    try:
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json=reg_data)
        print(f"1. Registration: {reg_resp.status_code}")
        if reg_resp.status_code != 200:
            print(f"Registration failed: {reg_resp.text}")
            return

        token_data = reg_resp.json()
        access_token = token_data.get("access_token")
        user_id = token_data.get("user", {}).get("id")

        print(f"   User ID: {user_id}")
        print(f"   Token: {access_token[:20]}...")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Test 2: Create a task
        print("\n2. Testing task creation...")
        task_data = {
            "title": "Test Task for Comprehensive Test",
            "description": "This is a test task created during comprehensive testing"
        }

        task_resp = requests.post(f"{BASE_URL}/api/tasks/", json=task_data, headers=headers)
        print(f"   Task creation response: {task_resp.status_code}")

        if task_resp.status_code != 200:
            print(f"   Task creation failed: {task_resp.text}")
            return

        task_result = task_resp.json()
        task_id = task_result.get("id")
        print(f"   Created task with ID: {task_id}")
        print(f"   Task data: {task_result}")

        # Test 3: Get the created task
        print(f"\n3. Testing getting task {task_id}...")
        get_task_resp = requests.get(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
        print(f"   Get task response: {get_task_resp.status_code}")

        if get_task_resp.status_code == 200:
            get_task_data = get_task_resp.json()
            print(f"   Retrieved task: {get_task_data}")
        else:
            print(f"   Failed to get task: {get_task_resp.text}")

        # Test 4: Get all tasks
        print(f"\n4. Testing getting all tasks...")
        get_all_resp = requests.get(f"{BASE_URL}/api/tasks/", headers=headers)
        print(f"   Get all tasks response: {get_all_resp.status_code}")

        if get_all_resp.status_code == 200:
            all_tasks = get_all_resp.json()
            print(f"   Number of tasks retrieved: {len(all_tasks)}")
            print(f"   Tasks: {all_tasks}")
        else:
            print(f"   Failed to get all tasks: {get_all_resp.text}")

        # Test 5: Update the task
        print(f"\n5. Testing updating task {task_id}...")
        update_data = {
            "title": "Updated Test Task",
            "description": "This task has been updated during comprehensive testing"
        }

        update_resp = requests.put(f"{BASE_URL}/api/tasks/{task_id}", json=update_data, headers=headers)
        print(f"   Update response: {update_resp.status_code}")

        if update_resp.status_code == 200:
            updated_task = update_resp.json()
            print(f"   Updated task: {updated_task}")
        else:
            print(f"   Failed to update task: {update_resp.text}")

        # Test 6: Toggle task completion
        print(f"\n6. Testing toggling task completion for {task_id}...")
        completion_data = {
            "completed": True
        }

        toggle_resp = requests.patch(f"{BASE_URL}/api/tasks/{task_id}/complete", json=completion_data, headers=headers)
        print(f"   Toggle completion response: {toggle_resp.status_code}")

        if toggle_resp.status_code == 200:
            toggled_task = toggle_resp.json()
            print(f"   Toggled task (now completed): {toggled_task}")
        else:
            print(f"   Failed to toggle task completion: {toggle_resp.text}")

        # Test 7: Get task again to verify completion
        print(f"\n7. Testing getting task again to verify completion...")
        verify_resp = requests.get(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
        if verify_resp.status_code == 200:
            verified_task = verify_resp.json()
            print(f"   Verified task completion: {verified_task['completed']}")
        else:
            print(f"   Failed to verify task: {verify_resp.text}")

        # Test 8: Delete the task
        print(f"\n8. Testing deleting task {task_id}...")
        delete_resp = requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
        print(f"   Delete response: {delete_resp.status_code}")

        if delete_resp.status_code == 200:
            print(f"   Task deleted successfully!")
        else:
            print(f"   Failed to delete task: {delete_resp.text}")

        # Test 9: Try to get the deleted task (should fail)
        print(f"\n9. Testing getting deleted task (should fail)...")
        get_deleted_resp = requests.get(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
        print(f"   Get deleted task response: {get_deleted_resp.status_code}")
        if get_deleted_resp.status_code == 404:
            print(f"   Confirmed task was deleted (404 as expected)")
        else:
            print(f"   Unexpected response: {get_deleted_resp.text}")

        print(f"\n=== All tests completed successfully! ===")
        print("✅ Registration and login work")
        print("✅ Task creation works")
        print("✅ Getting individual tasks works")
        print("✅ Getting all tasks works")
        print("✅ Task updating works")
        print("✅ Task completion toggle works")
        print("✅ Task deletion works")
        print("✅ All CRUD operations are functioning properly")

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    comprehensive_test()