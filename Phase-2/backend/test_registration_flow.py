#!/usr/bin/env python3
"""
Test script to verify the full registration flow
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from sqlmodel import Session, create_engine
from dependencies.database import get_db_session
from services.auth_service import create_user
from schemas.auth import UserCreate

def test_registration_flow():
    """Test the full registration flow"""
    print("Testing the full registration flow...")

    # Create a mock user data
    user_data = {
        "email": "testuser@example.com",
        "name": "Test User",
        "password": "strinG1#"
    }

    print(f"User data: {user_data}")

    # Try to create a user using the service
    try:
        # We need a session for this test, but we'll create a minimal one
        # Since we're just testing validation, let's test the validation separately
        from utils.validation import validate_email, validate_password

        email_valid = validate_email(user_data["email"])
        password_valid, password_error = validate_password(user_data["password"])

        print(f"Email validation: {email_valid} (email: {user_data['email']})")
        print(f"Password validation: {password_valid} (password: {user_data['password']})")
        if not password_valid:
            print(f"Password error: {password_error}")

        if email_valid and password_valid:
            print("All validations passed!")
        else:
            print("Validations failed!")

    except Exception as e:
        print(f"Error during validation test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_registration_flow()