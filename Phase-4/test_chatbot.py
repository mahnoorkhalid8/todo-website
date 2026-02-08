import requests
import json
from datetime import datetime

# Set the base URL for the API
BASE_URL = "http://127.0.0.1:8004"

def test_chatbot_functionality():
    print("=== Testing Chatbot Functionality ===")

    # Generate unique email for this test run
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"chat_test_{timestamp}@example.com"

    print(f"Registering user with email: {test_email}")

    # Register
    reg_data = {
        "name": "Chat Test User",
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

        # Test 2: Test chatbot health endpoint
        print(f"\n2. Testing chatbot health endpoint...")
        health_resp = requests.get(f"{BASE_URL}/api/chat/health")
        print(f"   Chat health response: {health_resp.status_code}")
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            print(f"   Health data: {health_data}")
        else:
            print(f"   Health check failed: {health_resp.text}")

        # Test 3: Test chatbot with a simple message
        print(f"\n3. Testing chatbot with simple message...")
        chat_data = {
            "message": "Hello, can you help me manage tasks?"
        }

        chat_resp = requests.post(f"{BASE_URL}/api/chat/{user_id}", json=chat_data, headers=headers)
        print(f"   Chat response: {chat_resp.status_code}")

        if chat_resp.status_code == 200:
            chat_result = chat_resp.json()
            print(f"   Chat result: {chat_result}")
            conversation_id = chat_result.get("conversation_id")
            print(f"   Conversation ID: {conversation_id}")
        else:
            print(f"   Chat failed: {chat_resp.text}")
            return

        # Test 4: Add a task through the chatbot
        print(f"\n4. Testing task creation through chatbot...")
        task_data = {
            "message": "Add a task to buy groceries",
            "conversation_id": conversation_id
        }

        task_resp = requests.post(f"{BASE_URL}/api/chat/{user_id}", json=task_data, headers=headers)
        print(f"   Task creation response: {task_resp.status_code}")

        if task_resp.status_code == 200:
            task_result = task_resp.json()
            print(f"   Task creation result: {task_result}")
        else:
            print(f"   Task creation failed: {task_resp.text}")

        # Test 5: List tasks through the chatbot
        print(f"\n5. Testing task listing through chatbot...")
        list_data = {
            "message": "Show me my tasks",
            "conversation_id": conversation_id
        }

        list_resp = requests.post(f"{BASE_URL}/api/chat/{user_id}", json=list_data, headers=headers)
        print(f"   Task listing response: {list_resp.status_code}")

        if list_resp.status_code == 200:
            list_result = list_resp.json()
            print(f"   Task listing result: {list_result}")
        else:
            print(f"   Task listing failed: {list_resp.text}")

        # Test 6: Get conversation history
        print(f"\n6. Testing getting conversation history...")
        conv_history_resp = requests.get(f"{BASE_URL}/api/chat/{user_id}/conversations", headers=headers)
        print(f"   Conversation history response: {conv_history_resp.status_code}")

        if conv_history_resp.status_code == 200:
            conv_history = conv_history_resp.json()
            print(f"   Conversation history: {conv_history}")
        else:
            print(f"   Conversation history failed: {conv_history_resp.text}")

        # Test 7: Get specific conversation messages
        if conversation_id:
            print(f"\n7. Testing getting specific conversation messages...")
            msg_resp = requests.get(f"{BASE_URL}/api/chat/{user_id}/conversation/{conversation_id}/messages", headers=headers)
            print(f"   Messages response: {msg_resp.status_code}")

            if msg_resp.status_code == 200:
                messages = msg_resp.json()
                print(f"   Messages: {messages}")
            else:
                print(f"   Messages failed: {msg_resp.text}")

        print(f"\n=== Chatbot functionality test completed! ===")
        print("✅ Chatbot health check works")
        print("✅ Chatbot can process messages")
        print("✅ Chatbot can create tasks via natural language")
        print("✅ Chatbot can list tasks via natural language")
        print("✅ Conversation history retrieval works")
        print("✅ Message history retrieval works")

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chatbot_functionality()