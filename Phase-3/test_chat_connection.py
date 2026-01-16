import requests
import json
from datetime import datetime

# Test the updated backend connection
BASE_URL = "http://127.0.0.1:8004"  # Updated port

def test_chat_connection():
    print("=== Testing Chat Connection with Updated Port ===")

    # Generate unique email for this test run
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"conn_test_{timestamp}@example.com"

    print(f"Registering user with email: {test_email}")

    # Register
    reg_data = {
        "name": "Connection Test User",
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

        # Test 2: Test chatbot with a simple message
        print(f"\n2. Testing chatbot connection...")
        chat_data = {
            "message": "Hello, can you help me create a task?"
        }

        chat_resp = requests.post(f"{BASE_URL}/api/chat/{user_id}", json=chat_data, headers=headers)
        print(f"   Chat response: {chat_resp.status_code}")

        if chat_resp.status_code == 200:
            chat_result = chat_resp.json()
            print(f"   ✓ Chat connection successful!")
            print(f"   Response: {chat_result['response'][:60]}...")
            print(f"   Conversation ID: {chat_result.get('conversation_id')}")

            # Test 3: Create a task through chat
            print(f"\n3. Testing task creation through chat...")
            task_data = {
                "message": "Add a task to test the chatbot connection",
                "conversation_id": chat_result.get('conversation_id')
            }

            task_resp = requests.post(f"{BASE_URL}/api/chat/{user_id}", json=task_data, headers=headers)
            print(f"   Task creation response: {task_resp.status_code}")

            if task_resp.status_code == 200:
                task_result = task_resp.json()
                print(f"   ✓ Task creation successful!")
                print(f"   Response: {task_result['response']}")
            else:
                print(f"   ✗ Task creation failed: {task_resp.text}")

        else:
            print(f"   ✗ Chat connection failed: {chat_resp.text}")
            print(f"   Status code: {chat_resp.status_code}")
            if chat_resp.status_code == 500:
                print("   This may indicate a server-side error")

        print(f"\n=== Connection test completed ===")
        print(f"If the connection is successful, the frontend should work properly!")
        print(f"Make sure to restart the frontend after updating the environment variables.")

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chat_connection()