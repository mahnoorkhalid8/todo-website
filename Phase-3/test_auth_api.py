import requests
import json

# Base URL for the backend
BASE_URL = "http://localhost:8000"

def test_api_connection():
    """Test if the API is reachable"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("+ Backend API is reachable")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"- Backend API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"- Could not reach backend API: {e}")
        return False

def get_openapi_schema():
    """Get the OpenAPI schema to understand the correct API endpoints"""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            print("+ Retrieved OpenAPI schema")

            # Look for auth endpoints
            paths = schema.get("paths", {})
            auth_paths = {path: methods for path, methods in paths.items() if "auth" in path.lower()}

            print("Auth endpoints found:")
            for path, methods in auth_paths.items():
                print(f"  {path}: {list(methods.keys())}")

            return schema
        else:
            print(f"Could not retrieve OpenAPI schema: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error retrieving OpenAPI schema: {e}")
        return None

def register_user_directly():
    """Try to register a user using the correct API format"""
    # First, let's try to see what the auth endpoints look like
    try:
        # Try to call the register endpoint with correct format
        register_url = f"{BASE_URL}/api/auth/register"

        # Based on the schemas, we need to send JSON data
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        payload = {
            "email": "testuser@example.com",
            "password": "securepassword123",
            "name": "Test User"
        }

        print(f"Attempting to register user with payload: {payload}")

        response = requests.post(
            register_url,
            headers=headers,
            json=payload
        )

        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print("\n" + "=" * 50)
                print("SUCCESS! JWT TOKEN RETRIEVED:")
                print(token)
                print("=" * 50)
                return token
            else:
                print("Registration successful but no token returned")
        else:
            print("Registration failed")

        return None

    except Exception as e:
        print(f"Error during registration attempt: {e}")
        return None

if __name__ == "__main__":
    print("Todo App JWT Token Retrieval")
    print("=" * 40)

    # Test API connection first
    if test_api_connection():
        print()

        # Get the API schema to understand endpoints
        schema = get_openapi_schema()
        print()

        # Try to register a user
        token = register_user_directly()

        if token:
            print(f"\nJWT Token: {token}")
        else:
            print("\nFailed to retrieve JWT token. The auth routes may have implementation issues.")
    else:
        print("Cannot connect to backend API. Please ensure the backend server is running on port 8000.")