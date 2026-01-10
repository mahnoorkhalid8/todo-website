#!/usr/bin/env python3
"""
Test script to check database connection and user existence
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from sqlmodel import Session, create_engine
from config import settings
from models import User

def test_database_connection():
    """Test database connection and check for existing users"""
    print("Testing database connection...")

    try:
        # Create engine using the same settings as the app
        engine = create_engine(settings.DATABASE_URL)

        # Create a session
        with Session(engine) as session:
            print("Database connection successful!")

            # Check if any users exist
            users = session.query(User).all()
            print(f"Number of users in database: {len(users)}")

            # Show existing emails if any
            for user in users:
                print(f"Existing user: {user.email} (ID: {user.id})")

            # Check if the test email exists
            test_email = "user@example.com"
            existing_user = session.query(User).filter(User.email == test_email).first()
            if existing_user:
                print(f"Email {test_email} already exists in database!")
                print(f"Existing user ID: {existing_user.id}")
            else:
                print(f"Email {test_email} is not in database - available for registration")

    except Exception as e:
        print(f"Database connection error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_connection()