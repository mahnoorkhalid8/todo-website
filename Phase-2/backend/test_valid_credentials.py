#!/usr/bin/env python3
"""
Test script to verify registration and login with valid credentials
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_valid_credentials():
    """Test with valid credentials that meet all requirements"""
    # Using a valid password that meets all requirements
    password = "Abcdef123!"  # 10 chars, upper, lower, digit, special
    email = "abc@gmail.com"
    username = "xyz"

    print(f"Testing with valid credentials:")
    print(f"  Email: {email}")
    print(f"  Password: {password} (length: {len(password)})")
    print(f"  Username: {username}")

    # Check if the password meets validation requirements
    from utils.validation import validate_password, validate_email

    is_valid, error_msg = validate_password(password)
    print(f"Password validation result: {is_valid}")
    if error_msg:
        print(f"Password error: {error_msg}")

    email_valid = validate_email(email)
    print(f"Email validation result: {email_valid}")

    if not is_valid or not email_valid:
        print("❌ Validation failed!")
        return False

    print("✅ Credentials pass validation!")

    # Test the complete registration and login flow
    try:
        from sqlmodel import Session
        from db import get_engine
        from services.auth_service import create_user, authenticate_user

        print("\nTesting complete registration and login flow...")

        # Connect to database
        engine = get_engine()

        with Session(engine) as session:
            # Delete existing user if exists (for clean test)
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
                print(f"  Registration successful! User ID: {new_user.id}")
            except Exception as e:
                print(f"  Registration failed: {e}")
                import traceback
                traceback.print_exc()
                return False

            # Try to login
            print("  Attempting login...")
            try:
                authenticated_user = authenticate_user(session, email, password)
                if authenticated_user:
                    print(f"  Login successful! User ID: {authenticated_user.id}")
                else:
                    print("  Login failed - invalid credentials")
                    return False
            except Exception as e:
                print(f"  Login failed with error: {e}")
                import traceback
                traceback.print_exc()
                return False

        print("\nComplete authentication flow test passed!")
        print("Registration and login are working properly with valid credentials.")
        return True

    except Exception as e:
        print(f"Database operation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_original_weak_password():
    """Test the originally requested weak password to show why it fails"""
    print("\n" + "="*50)
    print("Testing originally requested password 'Abc1!' (will fail):")

    password = "Abc1!"  # Too short
    email = "abc@gmail.com"
    username = "xyz"

    from utils.validation import validate_password

    is_valid, error_msg = validate_password(password)
    print(f"Password: {password} (length: {len(password)})")
    print(f"Validation result: {is_valid}")
    if error_msg:
        print(f"Error: {error_msg}")

    print("This is why registration with 'Abc1!' fails - it doesn't meet password requirements.")

if __name__ == "__main__":
    print("Testing authentication system with valid credentials...")

    # Test with weak password to explain why it fails
    test_original_weak_password()

    # Test with valid credentials
    success = test_valid_credentials()

    if success:
        print("\nSuccess! The authentication system is working correctly.")
        print("Use a password with at least 8 characters, including uppercase, lowercase, digit, and special character.")
    else:
        print("\nTests failed! There may still be issues with the authentication system.")