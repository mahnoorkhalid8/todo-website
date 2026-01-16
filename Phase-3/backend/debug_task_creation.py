import requests
import json

# Test creating a task with minimal data
def test_create_task():
    url = "http://localhost:8000/api/tasks/"

    # Sample headers (you might need to add an auth token if required)
    headers = {
        "Content-Type": "application/json",
        # If you're logged in, you'd need to add your auth token here:
        # "Authorization": "Bearer YOUR_TOKEN_HERE"
    }

    # Minimal task data
    task_data = {
        "title": "Test Task",
        "description": "This is a test description"
    }

    print("Attempting to create task...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(task_data, indent=2)}")

    try:
        response = requests.post(url, headers=headers, json=task_data)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")

        if response.status_code == 422:
            print("\nValidation Error Details:")
            try:
                error_detail = response.json()
                print(json.dumps(error_detail, indent=2))
            except:
                print("Could not parse error details as JSON")

    except requests.exceptions.ConnectionError:
        print("Connection error - is the server running?")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_create_task()