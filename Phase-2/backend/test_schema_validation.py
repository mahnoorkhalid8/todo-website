#!/usr/bin/env python3
"""
Test script to validate the UserCreate schema directly
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from schemas.auth import UserCreate
from pydantic import ValidationError

def test_user_create_schema():
    """Test the UserCreate schema directly"""
    print("Testing UserCreate schema...")

    # Test data that should work
    valid_data = {
        "email": "user@example.com",
        "name": "string",
        "password": "strinG1#"
    }

    print(f"Testing with data: {valid_data}")

    try:
        # Create a UserCreate instance - this should trigger validation
        user_create = UserCreate(**valid_data)
        print(f"UserCreate instance created successfully: {user_create}")
        print(f"Email: {user_create.email}")
        print(f"Name: {user_create.name}")
        print(f"Password: {user_create.password}")

    except ValidationError as ve:
        print(f"ValidationError occurred: {ve}")
        print("Validation errors:")
        for error in ve.errors():
            print(f"  - {error['loc']}: {error['msg']} (type: {error['type']})")

    except Exception as e:
        print(f"Other error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_create_schema()