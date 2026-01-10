#!/usr/bin/env python3
"""
Test script to simulate the complete registration process step by step
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from sqlmodel import Session, create_engine
from config import settings
from models import User
from utils.validation import validate_email, validate_password
from utils.auth import get_password_hash
from services.auth_service import create_user

def test_complete_registration():
    """Test the complete registration process step by step"""
    print("Testing complete registration process...")

    # Test data
    email = "user@example.com"
    password = "strinG1#"
    name = "string"

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

    # Step 3: Check if user already exists
    print("\nStep 3: Checking if user already exists...")
    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as session:
        existing_user = session.query(User).filter(User.email == email).first()
        print(f"User already exists: {existing_user is not None}")
        if existing_user:
            print("USER ALREADY EXISTS - REGISTRATION WOULD FAIL HERE")
            return

    # Step 4: Hash password (this is where the bcrypt error might occur)
    print("\nStep 4: Hashing password...")
    try:
        hashed_password = get_password_hash(password)
        print(f"Password hashed successfully: {hashed_password[:20]}...")
    except Exception as e:
        print(f"PASSWORD HASHING FAILED: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 5: Create user using the service (this is where it would fail in the API)
    print("\nStep 5: Creating user via service...")
    try:
        with Session(engine) as session:
            db_user = create_user(session, email, password, name)
            print(f"User created successfully: {db_user.email}")
            print(f"User ID: {db_user.id}")
    except Exception as e:
        print(f"USER CREATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\nALL STEPS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    test_complete_registration()