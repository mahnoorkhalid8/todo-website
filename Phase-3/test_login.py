import requests
import json

def test_login():
    """
    Test login functionality for the specific user
    """
    print("Testing login for user: mahnoorkhalid814@gmail.com")
    print("="*60)

    # Test if the backend is accessible
    try:
        health_response = requests.get("http://127.0.0.1:8000/health", timeout=10)
        if health_response.status_code == 200:
            print("[OK] Backend is accessible")
        else:
            print(f"[ERROR] Backend health check failed: {health_response.status_code}")
            return
    except Exception as e:
        print(f"[ERROR] Cannot reach backend: {e}")
        return

    # Attempt login with the known user
    login_payload = {
        "email": "mahnoorkhalid814@gmail.com",
        "password": "SecurePass123!"  # Using a common test password
    }

    print(f"Attempting login with email: {login_payload['email']}")

    try:
        response = requests.post("http://127.0.0.1:8000/api/auth/login", json=login_payload, timeout=15)

        print(f"Login response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Login successful!")
            print(f"Token received: {data.get('access_token', '')[:30]}...")
            print(f"User info: {data.get('user', {})}")
        elif response.status_code == 401:
            print("[ERROR] Incorrect email or password")
            print("The user exists in the database but the password might be incorrect")
        elif response.status_code == 422:
            print("[ERROR] Validation error - check email/password format")
            print(f"Response: {response.text}")
        else:
            print(f"[ERROR] Login failed with status {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection error - backend might be down or unreachable")
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out - backend might be slow to respond")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

    print("\nNote: If the password is unknown, you may need to reset it or register with a known password.")

def test_cors_issues():
    """
    Test for potential CORS issues that might cause 'failed to fetch' errors
    """
    print("\nTesting for potential CORS issues...")

    # Try with proper headers that a browser would send
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "http://localhost:3000",
        "Referer": "http://localhost:3000/"
    }

    login_payload = {
        "email": "mahnoorkhalid814@gmail.com",
        "password": "SecurePass123!"
    }

    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/auth/login",
            json=login_payload,
            headers=headers,
            timeout=15
        )
        print(f"CORS test response status: {response.status_code}")
    except Exception as e:
        print(f"CORS test failed: {e}")

if __name__ == "__main__":
    test_login()
    test_cors_issues()