import requests
import json

# Base URL for the backend
BASE_URL = "http://localhost:8000"

def try_register_with_query_params():
    """Try to register using query parameters as the API currently expects"""
    register_url = f"{BASE_URL}/api/auth/register"

    # Try sending data as query parameters based on the error we're seeing
    params = {
        "user": json.dumps({
            "email": "testuser@example.com",
            "password": "securepassword123",
            "name": "Test User"
        })
    }

    print(f"Attempting to register using query parameters: {params}")

    try:
        response = requests.post(register_url, params=params)
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
    except Exception as e:
        print(f"Error: {e}")

    return None

def try_register_with_form_data():
    """Try to register using form data"""
    register_url = f"{BASE_URL}/api/auth/register"

    # Try sending data as form data with user as a JSON string
    form_data = {
        "user": json.dumps({
            "email": "testuser2@example.com",
            "password": "anotherpassword123",
            "name": "Test User 2"
        })
    }

    print(f"Attempting to register using form data: {form_data}")

    try:
        response = requests.post(register_url, data=form_data)
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
    except Exception as e:
        print(f"Error: {e}")

    return None

if __name__ == "__main__":
    print("Trying alternative approaches to register with the current API...")
    print("=" * 60)

    print("\n1. Trying query parameters approach:")
    token1 = try_register_with_query_params()

    print("\n2. Trying form data approach:")
    token2 = try_register_with_form_data()

    if not token1 and not token2:
        print("\n" + "=" * 60)
        print("FAILED: Could not register user with current API implementation")
        print("The backend routes still need to be fixed properly")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("SUCCESS: Got JWT token using workaround!")
        print("=" * 60)