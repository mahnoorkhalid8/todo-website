#!/usr/bin/env python3
"""
Script to check existing password hashes in the database
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from sqlmodel import Session
from config import settings
from models import User

def check_existing_hashes():
    """Check existing password hashes in the database"""
    print("Checking existing password hashes in database...")

    try:
        from db import get_engine

        # Create engine using the same settings as the app
        engine = get_engine()

        # Create a session
        with Session(engine) as session:
            print("Database connection successful!")

            # Check if any users exist
            users = session.query(User).all()
            print(f"Number of users in database: {len(users)}")

            # Show existing users and check their password hash format
            for user in users:
                print(f"User: {user.email} (ID: {user.id})")
                print(f"  Password hash format: {user.password_hash[:10]}..." if user.password_hash else "  No password hash")

                # Check if hash looks like a valid bcrypt hash
                if user.password_hash and user.password_hash.startswith('$2'):
                    print(f"  SUCCESS: Appears to be a valid bcrypt hash")

                    # Try to verify a test password against this hash (should fail)
                    from utils.auth import verify_password
                    test_result = verify_password("invalid_password", user.password_hash)
                    print(f"  Test verification result: {test_result} (expected: False)")
                else:
                    print(f"  UNKNOWN: Unknown hash format")
                print()

    except Exception as e:
        print(f"Error checking database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_existing_hashes()