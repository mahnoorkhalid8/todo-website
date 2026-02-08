#!/usr/bin/env python3
"""
Simple test script to verify bcrypt functionality works properly after fixes
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_bcrypt_simple():
    """Simple test that bcrypt functionality works properly"""
    print("Testing bcrypt functionality after fixes...")

    try:
        # Import the auth utilities
        from utils.auth import get_password_hash, verify_password

        print("SUCCESS: Successfully imported auth utilities")

        # Test password hashing
        test_password = "TestPass123!"
        print(f"Testing with password: {test_password}")

        # Hash the password
        hashed = get_password_hash(test_password)
        print(f"SUCCESS: Password hashed successfully: {hashed[:20]}...")

        # Verify the password
        is_valid = verify_password(test_password, hashed)
        print(f"SUCCESS: Password verification result: {is_valid}")

        if is_valid:
            print("SUCCESS: Password hashing and verification working correctly!")
        else:
            print("FAILURE: Password verification failed!")
            return False

        # Test with wrong password
        is_invalid = verify_password("WrongPassword123!", hashed)
        print(f"SUCCESS: Wrong password verification result: {is_invalid}")

        if not is_invalid:
            print("SUCCESS: Correctly rejected wrong password!")
        else:
            print("FAILURE: Failed to reject wrong password!")
            return False

        return True

    except Exception as e:
        print(f"FAILURE: Error during bcrypt functionality test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bcrypt_simple()
    if success:
        print("\nSUCCESS: All bcrypt functionality tests passed!")
    else:
        print("\nFAILURE: Bcrypt functionality tests failed!")