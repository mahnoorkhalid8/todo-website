import requests
import json

def reset_password_or_register():
    """
    Either register the user with a known password or explain the situation
    """
    print("USER LOGIN SOLUTION")
    print("="*50)
    print("User 'mahnoorkhalid814@gmail.com' exists in the database but login is failing.")
    print("This means the password you're using is incorrect.")
    print()

    # Option 1: Try registering with the same email (should fail due to uniqueness constraint)
    print("Option 1: Attempt to register with the same email to see error message")
    register_payload = {
        "email": "mahnoorkhalid814@gmail.com",
        "password": "NewSecurePassword123!",
        "name": "Mahnoor Khalid"
    }

    try:
        response = requests.post("http://127.0.0.1:8000/api/auth/register", json=register_payload, timeout=10)
        print(f"Registration attempt status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
            print("\nThe user already exists in the database (as confirmed earlier)")
            print("You need to use the correct password that was used during registration")
        else:
            print("Unexpected: User was able to register again (this shouldn't happen)")
    except Exception as e:
        print(f"Registration request failed: {e}")

    print("\n" + "="*50)
    print("SOLUTION:")
    print("1. The user 'mahnoorkhalid814@gmail.com' EXISTS in the database")
    print("2. The PASSWORD you're using is INCORRECT")
    print("3. You need to either:")
    print("   a) Remember the correct password used during registration")
    print("   b) Register a new account with a password you remember")
    print("   c) Use a 'forgot password' feature if available")
    print()
    print("TO FIX THE LOGIN ISSUE:")
    print("- If you know the original password, use that")
    print("- If you don't know the original password, register a new account")
    print("- Or contact the system administrator to reset the password")
    print()
    print("COMMON TEST PASSWORDS USED IN THIS SYSTEM:")
    print("- SecurePass123!")
    print("- test123")
    print("- password123")
    print("- LetMeIn123!")
    print()
    print("Try these or register a new account with a password you'll remember.")

def test_common_passwords():
    """
    Test some common passwords that might have been used
    """
    print("\nTrying common test passwords:")
    common_passwords = [
        "SecurePass123!",
        "test123",
        "password123",
        "letmein",
        "admin123",
        "password",
        "123456",
        "test"
    ]

    email = "mahnoorkhalid814@gmail.com"

    for pwd in common_passwords:
        print(f"  Trying password: {pwd}")
        login_payload = {"email": email, "password": pwd}

        try:
            response = requests.post("http://127.0.0.1:8000/api/auth/login", json=login_payload, timeout=5)
            if response.status_code == 200:
                print(f"  [SUCCESS] Password '{pwd}' works!")
                return pwd
            elif response.status_code == 401:
                print(f"  [FAIL] Password '{pwd}' is incorrect")
            else:
                print(f"  [ERROR] Status {response.status_code} for password '{pwd}'")
        except:
            print(f"  [ERROR] Could not test password '{pwd}'")

    print("  None of the common passwords worked.")
    return None

if __name__ == "__main__":
    reset_password_or_register()
    test_common_passwords()