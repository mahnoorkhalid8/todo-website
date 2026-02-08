#!/usr/bin/env python3
"""
Test script to verify user registration works with corrected SQLModel syntax
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_registration():
    """Test user registration to verify it saves to Neon database"""
    try:
        print("=== Testing User Registration ===")

        # Import necessary modules
        from config import settings
        print(f"DATABASE_URL from settings: {settings.DATABASE_URL}")

        # Check if it contains neon.tech (indicating Neon DB)
        if "neon.tech" in settings.DATABASE_URL:
            print("[SUCCESS] Confirmed: Using Neon database URL")
        else:
            print("[ERROR] Warning: Not using Neon database URL")
            return False

        # Import the auth service
        from services.auth_service import create_user
        from db import get_session
        import uuid
        from models import User

        # Create a test user
        test_email = f"test_{str(uuid.uuid4())[:8]}@example.com"
        test_password = "TestPassword123!"
        test_name = "Test User"

        print(f"Attempting to create test user: {test_email}")

        # Use the session context manager to create the user
        with get_session() as session:
            try:
                # Create the user using the auth service
                created_user = create_user(session, test_email, test_password, test_name)
                print(f"[SUCCESS] User created: {created_user.email}")

                # Verify the user was created by querying for it
                from sqlmodel import select
                from services.auth_service import authenticate_user

                # Try to authenticate the user to verify it was saved
                authenticated_user = authenticate_user(session, test_email, test_password)
                if authenticated_user:
                    print(f"[SUCCESS] User can be authenticated: {authenticated_user.email}")
                else:
                    print("[ERROR] Failed to authenticate the created user")
                    return False

                # Clean up: delete the test user
                session.delete(authenticated_user)
                session.commit()
                print("[SUCCESS] Test user cleaned up successfully")

            except Exception as e:
                print(f"[ERROR] Error during user creation: {e}")
                import traceback
                traceback.print_exc()
                return False

        print("\n[SUCCESS] Registration test completed successfully!")
        return True

    except Exception as e:
        print(f"[ERROR] Error testing registration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_registration()
    if success:
        print("\n[SUCCESS] Registration functionality verified successfully!")
    else:
        print("\n[ERROR] Registration functionality test failed!")
        sys.exit(1)