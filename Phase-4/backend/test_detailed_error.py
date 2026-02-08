import os
import sys
import traceback
from fastapi.testclient import TestClient
from main import app

# Set environment variables
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_1wiNqRWc4MPh@ep-sparkling-term-a4onppqn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'
os.environ['JWT_SECRET'] = 'o2nmkwIUqotG5dDCWR0a0rk2Uk2rL0DPBvqbdkwZ54N'

print("Creating test client...")

try:
    client = TestClient(app)

    # Test registration first
    print("\n1. Testing registration...")
    response = client.post("/api/auth/register", json={
        "name": "Test User",
        "email": f"test_detailed_{int(__import__('time').time())}@example.com",
        "password": "SecurePass123!"
    })
    print(f"Registration response: {response.status_code}")
    print(f"Registration data: {response.json()}")

    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"Got token: {token[:20]}...")

        # Test task creation
        print("\n2. Testing task creation...")
        headers = {"Authorization": f"Bearer {token}"}
        task_response = client.post("/api/tasks/",
                                  json={"title": "Test Task", "description": "Test Description"},
                                  headers=headers)
        print(f"Task creation response: {task_response.status_code}")
        if task_response.status_code != 200:
            print(f"Task creation error: {task_response.text}")

        # Test getting tasks
        print("\n3. Testing get tasks...")
        get_response = client.get("/api/tasks/", headers=headers)
        print(f"Get tasks response: {get_response.status_code}")
        if get_response.status_code != 200:
            print(f"Get tasks error: {get_response.text}")

except Exception as e:
    print(f"Error occurred: {e}")
    traceback.print_exc()