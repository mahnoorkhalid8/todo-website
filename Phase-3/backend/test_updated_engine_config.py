#!/usr/bin/env python3
"""
Test script to check how the database engine is configured after fix
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_updated_engine_config():
    """Test how the database engine is configured after the fix"""
    print("Testing updated database engine configuration...")

    # Import the updated get_engine function
    from db import get_engine
    from config import settings

    print(f"Config settings DATABASE_URL: {settings.DATABASE_URL}")
    print(f"Environment DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')}")

    # Check if Neon is detected
    # Use the same logic as in the updated db.py
    try:
        from db import settings as db_settings
        DATABASE_URL = db_settings.DATABASE_URL
    except ImportError:
        DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/todo_app")

    print(f"Using DATABASE_URL: {DATABASE_URL}")
    print(f"Contains 'neon.tech': {'neon.tech' in DATABASE_URL}")

    # Create engine
    print("\nCreating engine...")
    try:
        engine = get_engine()
        print(f"Engine created successfully")
        print(f"Engine URL (first 50 chars): {str(engine.url)[:50]}...")

        # Test a simple connection
        with engine.connect() as conn:
            print("Direct engine connection successful!")
            print("Neon database connection is working!")

    except Exception as e:
        print(f"Engine creation/connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_updated_engine_config()