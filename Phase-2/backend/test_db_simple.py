#!/usr/bin/env python3
"""
Simple test script to verify Neon database connection and operations
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_operations():
    """Test database operations to verify Neon connection is working"""
    try:
        print("=== Testing Neon Database Connection ===")

        # Import necessary modules
        from config import settings
        print(f"DATABASE_URL from settings: {settings.DATABASE_URL}")

        # Check if it contains neon.tech (indicating Neon DB)
        if "neon.tech" in settings.DATABASE_URL:
            print("[SUCCESS] Confirmed: Using Neon database URL")
        else:
            print("[ERROR] Warning: Not using Neon database URL")
            return False

        # Test database engine creation
        from db import get_engine
        engine = get_engine()
        print("[SUCCESS] Database engine created successfully")

        # Test creating a session and performing operations
        from sqlmodel import Session
        from models import User
        import uuid
        from utils.auth import get_password_hash

        with Session(engine) as session:
            print("[SUCCESS] Database session created successfully")

            # Test inserting a user
            test_email = f"test_{str(uuid.uuid4())[:8]}@example.com"
            test_user = User(
                id=str(uuid.uuid4()),
                email=test_email,
                name="Test User",
                password_hash=get_password_hash("TestPassword123!")
            )

            print(f"Attempting to create test user: {test_email}")
            session.add(test_user)
            session.commit()
            print("[SUCCESS] Test user created successfully")

            # Test querying the user back
            from sqlmodel import select
            retrieved_user = session.exec(select(User).where(User.email == test_email)).first()
            if retrieved_user:
                print(f"[SUCCESS] Successfully retrieved user from database: {retrieved_user.email}")

                # Clean up test user
                session.delete(retrieved_user)
                session.commit()
                print("[SUCCESS] Test user cleaned up successfully")
            else:
                print("[ERROR] Failed to retrieve user from database")
                return False

        print("\n[SUCCESS] All database operations completed successfully!")
        print("[SUCCESS] Neon database connection is working properly!")
        return True

    except Exception as e:
        print(f"[ERROR] Error testing database operations: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_operations()
    if success:
        print("\n[SUCCESS] Neon database connection verified successfully!")
    else:
        print("\n[ERROR] Neon database connection test failed!")
        sys.exit(1)