import requests
import json
from datetime import datetime

# Test the updated backend connection
BASE_URL = "http://127.0.0.1:8004"  # Updated port

def test_chat_connection():
    print("=== Testing Chat Connection with Updated Port ===")

    # Generate unique email for this test run
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"simple_test_{timestamp}@example.com"

    print(f"Registering user with email: {test_email}")

    # Register
    reg_data = {
        "name": "Simple Test User",
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

        # Test chatbot with a simple message
        print(f"\n2. Testing chatbot connection...")
        chat_data = {
            "message": "Hello, can you help me create a task?"
        }

        chat_resp = requests.post(f"{BASE_URL}/api/chat/{user_id}", json=chat_data, headers=headers)
        print(f"   Chat response: {chat_resp.status_code}")

        if chat_resp.status_code == 200:
            chat_result = chat_resp.json()
            print(f"   SUCCESS: Chat connection working!")
            print(f"   Response preview: {chat_result['response'][:50]}...")
            print(f"   Conversation ID: {chat_result.get('conversation_id')}")

            # Test task creation through chat
            print(f"\n3. Testing task creation through chat...")
            task_data = {
                "message": "Add a task to test the connection",
                "conversation_id": chat_result.get('conversation_id')
            }

            task_resp = requests.post(f"{BASE_URL}/api/chat/{user_id}", json=task_data, headers=headers)
            print(f"   Task creation response: {task_resp.status_code}")

            if task_resp.status_code == 200:
                task_result = task_resp.json()
                print(f"   SUCCESS: Task creation working!")
                print(f"   Response: {task_result['response']}")
            else:
                print(f"   ERROR: Task creation failed: {task_resp.text}")

        else:
            print(f"   ERROR: Chat connection failed: {chat_resp.text}")
            print(f"   Status code: {chat_resp.status_code}")

        print(f"\n=== Connection test completed ===")
        print(f"Backend API is accessible at {BASE_URL}")
        print(f"Frontend should connect properly once restarted with new environment settings.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    test_chat_connection()