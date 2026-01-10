#!/usr/bin/env python3
"""
Test script to simulate the registration process with Neon database
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from sqlmodel import Session
from config import settings
from models import User
from utils.validation import validate_email, validate_password
from services.auth_service import create_user

def test_neon_registration():
    """Test the registration process with Neon database"""
    print("Testing registration process with Neon database...")

    # Test data
    email = "testuser2@example.com"  # Using a different email to avoid conflicts
    password = "strinG1#"
    name = "Test User"

    print(f"Testing registration with: email={email}, password={password}, name={name}")

    # Step 1: Validate email
    print("\nStep 1: Validating email...")
    email_valid = validate_email(email)
    print(f"Email validation result: {email_valid}")
    if not email_valid:
        print("EMAIL VALIDATION FAILED")
        return

    # Step 2: Validate password
    print("\nStep 2: Validating password...")
    password_valid, password_error = validate_password(password)
    print(f"Password validation result: {password_valid}")
    print(f"Password error (if any): {password_error}")
    if not password_valid:
        print("PASSWORD VALIDATION FAILED")
        return

    # Step 3: Create user using the service
    print("\nStep 3: Creating user via service with Neon database...")
    try:
        # Use the dependency to get a proper session
        from dependencies.database import get_db_session

        # Get a session using the generator
        session_gen = get_db_session()
        session = next(session_gen)

        try:
            # Check if user already exists first
            existing_user = session.query(User).filter(User.email == email).first()
            print(f"User already exists: {existing_user is not None}")

            if existing_user:
                print("USER ALREADY EXISTS - deleting for test...")
                session.delete(existing_user)
                session.commit()
                print("Deleted existing user")

            # Now create the user
            db_user = create_user(session, email, password, name)
            session.commit()
            print(f"User created successfully: {db_user.email}")
            print(f"User ID: {db_user.id}")

        finally:
            # Close the session
            session.close()

    except Exception as e:
        print(f"USER CREATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\nREGISTRATION PROCESS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    test_neon_registration()