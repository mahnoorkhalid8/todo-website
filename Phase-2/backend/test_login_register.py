#!/usr/bin/env python3
"""
Test script to verify registration and login with specific credentials
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_credentials():
    """Test the specific credentials provided"""
    print("Testing credentials: email=abc@gmail.com, password=Abc1!, username=xyz")

    # First, let's check if the password meets validation requirements
    from utils.validation import validate_password, validate_email

    password = "Abc1!"
    email = "abc@gmail.com"
    username = "xyz"

    print(f"Password: {password} (length: {len(password)})")
    print(f"Email: {email}")
    print(f"Username: {username}")

    # Check password validation
    is_valid, error_msg = validate_password(password)
    print(f"Password validation result: {is_valid}")
    if error_msg:
        print(f"Password error: {error_msg}")

    # Check email validation
    email_valid = validate_email(email)
    print(f"Email validation result: {email_valid}")

    if not is_valid:
        print("❌ Password does not meet requirements!")
        print("Password must be at least 8 characters with uppercase, lowercase, digit, and special character")
        return False

    if not email_valid:
        print("❌ Email is not valid!")
        return False

    print("✅ Credentials pass validation!")

    # Now test the complete registration and login flow
    try:
        from sqlmodel import Session
        from db import get_engine
        from services.auth_service import create_user, authenticate_user

        print("\nTesting complete registration and login flow...")

        # Connect to database
        engine = get_engine()

        with Session(engine) as session:
            # Try to delete existing user if exists (for clean test)
            from models import User
            existing_user = session.query(User).filter(User.email == email).first()
            if existing_user:
                print("  Found existing user, deleting for clean test...")
                session.delete(existing_user)
                session.commit()

            # Register new user
            print("  Attempting registration...")
            try:
                new_user = create_user(session, email, password, username)
                session.commit()
                print(f"  ✅ Registration successful! User ID: {new_user.id}")
            except Exception as e:
                print(f"  ❌ Registration failed: {e}")
                return False

            # Try to login
            print("  Attempting login...")
            try:
                authenticated_user = authenticate_user(session, email, password)
                if authenticated_user:
                    print(f"  ✅ Login successful! User ID: {authenticated_user.id}")
                else:
                    print("  ❌ Login failed - invalid credentials")
                    return False
            except Exception as e:
                print(f"  ❌ Login failed with error: {e}")
                return False

        print("\n🎉 Complete authentication flow test passed!")
        print("Registration and login are working properly with the provided credentials.")
        return True

    except Exception as e:
        print(f"❌ Database operation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_credentials()
    if success:
        print("\n✅ All tests passed! The system is working correctly.")
    else:
        print("\n❌ Tests failed! There are issues with the authentication system.")