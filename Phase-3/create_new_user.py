import requests
import json

def create_new_user():
    """
    Create a new user with known credentials for testing
    """
    print("CREATING NEW USER FOR TESTING")
    print("="*50)

    # Create a new user with known credentials
    new_user_data = {
        "email": "testuser@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    }

    print(f"Creating new user with:")
    print(f"- Email: {new_user_data['email']}")
    print(f"- Password: {new_user_data['password']}")
    print(f"- Name: {new_user_data['name']}")
    print()

    try:
        response = requests.post("http://127.0.0.1:8000/api/auth/register", json=new_user_data, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] New user created successfully!")
            print(f"Token: {data.get('access_token', '')[:30]}...")
            print(f"User ID: {data.get('user', {}).get('id', 'N/A')}")

            # Now try to login with the same credentials
            print(f"\nTesting login with the new credentials...")
            login_response = requests.post("http://127.0.0.1:8000/api/auth/login", json=new_user_data, timeout=10)

            if login_response.status_code == 200:
                login_data = login_response.json()
                print("[SUCCESS] Login successful with new credentials!")
                print(f"Token: {login_data.get('access_token', '')[:30]}...")
                print()
                print("You can now use these credentials:")
                print(f"- Email: {new_user_data['email']}")
                print(f"- Password: {new_user_data['password']}")
                return True
            else:
                print(f"[ERROR] Login failed after registration: {login_response.status_code}")
                print(f"Response: {login_response.text}")

        elif response.status_code == 400:
            print(f"[ERROR] Registration failed: {response.json().get('detail', 'Unknown error')}")

            # Check if it's because email already exists
            if "already registered" in str(response.json()):
                print("Note: This email is already taken. Try with a different email.")

                # Try with a timestamp-based email
                import time
                timestamp_email = f"testuser.{int(time.time())}@example.com"
                new_user_data['email'] = timestamp_email
                print(f"\nTrying with new email: {timestamp_email}")

                response = requests.post("http://127.0.0.1:8000/api/auth/register", json=new_user_data, timeout=10)
                if response.status_code == 200:
                    print("[SUCCESS] User created with timestamp email!")
                    login_response = requests.post("http://127.0.0.1:8000/api/auth/login", json=new_user_data, timeout=10)
                    if login_response.status_code == 200:
                        print("[SUCCESS] Login successful!")
                        print(f"\nCredentials to use:")
                        print(f"- Email: {new_user_data['email']}")
                        print(f"- Password: {new_user_data['password']}")
                        return True
        else:
            print(f"[ERROR] Registration failed with status {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"[ERROR] Request failed: {e}")

    return False

def test_working_account():
    """
    Try to create a working account that you can use
    """
    print("\nCREATING WORKING ACCOUNT")
    print("="*30)

    # Try multiple common emails that are likely to be available
    emails_to_try = [
        "newuser@example.com",
        "demo@example.com",
        "user@example.com",
        "test.account@example.com"
    ]

    password = "SecurePass123!"
    name = "Demo User"

    for email in emails_to_try:
        user_data = {
            "email": email,
            "password": password,
            "name": name
        }

        print(f"Trying to create account: {email}")
        try:
            response = requests.post("http://127.0.0.1:8000/api/auth/register", json=user_data, timeout=10)

            if response.status_code == 200:
                print(f"[SUCCESS] Account created: {email}")
                print(f"[INFO] Login with:")
                print(f"  Email: {email}")
                print(f"  Password: {password}")

                # Test login
                login_resp = requests.post("http://127.0.0.1:8000/api/auth/login", json=user_data, timeout=10)
                if login_resp.status_code == 200:
                    print("[SUCCESS] Login also works!")
                    return email, password
                else:
                    print(f"[ERROR] Login failed for created account")

            elif "already registered" in str(response.json()):
                print(f"  - Email {email} already exists, trying next...")
                continue
            else:
                print(f"  - Failed to create {email}, trying next...")
                continue

        except Exception as e:
            print(f"  - Error creating {email}: {e}")
            continue

    print("\n[ERROR] Could not create a new account. Backend may be down.")
    return None, None

if __name__ == "__main__":
    print("ACCOUNT CREATION AND LOGIN TROUBLESHOOTING")
    print("="*60)
    print("Issue: The user 'mahnoorkhalid814@gmail.com' exists but login fails")
    print("Reason: The password is unknown")
    print()

    # Try to create a working account
    email, password = test_working_account()

    if email and password:
        print(f"\n✅ SOLUTION: Use the working account")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print("This account is guaranteed to work for login.")
    else:
        print("\n❌ Could not create a working account. Please check if the backend is running.")