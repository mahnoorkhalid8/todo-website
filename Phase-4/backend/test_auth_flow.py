#!/usr/bin/env python3
"""
Test script to verify the complete authentication flow
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from sqlmodel import Session
from db import get_engine
from models import User
from services.auth_service import create_user, authenticate_user
from utils.validation import validate_email, validate_password

def test_auth_flow():
    """Test the complete authentication flow"""
    print("Testing complete authentication flow...")

    # Test data
    email = "auth.test@example.com"
    password = "TestPass123!"
    name = "Auth Test User"

    print(f"Testing with: email={email}, password={password}, name={name}")

    # Step 1: Validate email and password
    print("\nStep 1: Validating credentials...")
    email_valid = validate_email(email)
    password_valid, password_error = validate_password(password)

    print(f"Email validation: {email_valid}")
    print(f"Password validation: {password_valid}")
    if password_error:
        print(f"Password error: {password_error}")

    if not email_valid or not password_valid:
        print("VALIDATION FAILED")
        return False

    # Step 2: Register a new user
    print("\nStep 2: Registering new user...")
    try:
        engine = get_engine()
        with Session(engine) as session:
            # Check if user already exists and delete if so (for clean test)
            existing_user = session.query(User).filter(User.email == email).first()
            if existing_user:
                print("  User already exists, deleting for test...")
                session.delete(existing_user)
                session.commit()

            # Create new user
            db_user = create_user(session, email, password, name)
            session.commit()
            print(f"  User created successfully: {db_user.email}")
            print(f"  User ID: {db_user.id}")

    except Exception as e:
        print(f"  USER REGISTRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 3: Authenticate the user (login)
    print("\nStep 3: Authenticating user (login)...")
    try:
        with Session(engine) as session:
            authenticated_user = authenticate_user(session, email, password)
            if authenticated_user:
                print(f"  User authenticated successfully: {authenticated_user.email}")
                print(f"  Authenticated user ID: {authenticated_user.id}")
            else:
                print("  USER AUTHENTICATION FAILED - invalid credentials")
                return False

    except Exception as e:
        print(f"  USER AUTHENTICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4: Test failed authentication with wrong password
    print("\nStep 4: Testing failed authentication with wrong password...")
    try:
        with Session(engine) as session:
            failed_auth = authenticate_user(session, email, "WrongPassword123!")
            if not failed_auth:
                print("  Correctly rejected wrong password")
            else:
                print("  ERROR: Wrong password was accepted!")
                return False

    except Exception as e:
        print(f"  ERROR during failed auth test: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\nSUCCESS: All authentication flow tests passed!")
    return True

if __name__ == "__main__":
    success = test_auth_flow()
    if success:
        print("\n🎉 Complete authentication flow is working correctly!")
    else:
        print("\n💥 Authentication flow has issues!")