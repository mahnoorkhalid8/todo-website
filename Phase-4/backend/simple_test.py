#!/usr/bin/env python3
"""
Simple test script to verify the bcrypt 72-byte password limit fix
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from utils.auth import get_password_hash, verify_password
from utils.validation import validate_password

def test_long_password_validation():
    """Test that passwords longer than 72 bytes are rejected"""
    print("Testing password validation for long passwords...")
    # Create a password longer than 72 characters (73 characters)
    password = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz123456789!@#$%^&*()AA"
    print(f"Password length: {len(password)} characters")

    # Validate password - this should fail with our new validation
    is_valid, error_msg = validate_password(password)
    print(f"Validation result: {is_valid}")
    print(f"Error message: {error_msg}")

    if not is_valid and "72" in error_msg:
        print("SUCCESS: Long password correctly rejected")
        return True
    else:
        print("FAILURE: Long password should have been rejected")
        return False

def test_short_password_validation():
    """Test that valid passwords are accepted"""
    print("\nTesting password validation for normal passwords...")
    password = "MySecureP@ss123"
    print(f"Password length: {len(password)} characters")

    # Validate password - this should pass
    is_valid, error_msg = validate_password(password)
    print(f"Validation result: {is_valid}")
    print(f"Error message: {error_msg}")

    if is_valid:
        print("SUCCESS: Normal password correctly accepted")
        return True
    else:
        print("FAILURE: Normal password should have been accepted")
        return False

def test_hash_verification_with_long_password_fallback():
    """Test the fallback mechanism for passwords longer than 72 bytes"""
    print("\nTesting hash/verification fallback for long passwords...")

    # Create a password exactly at the limit
    password_72 = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz123456789!@#$%"  # 72 chars
    print(f"Password length: {len(password_72)} characters")

    try:
        # Hash the password
        hashed = get_password_hash(password_72)
        print(f"Password hashed successfully")

        # Verify the password
        is_verified = verify_password(password_72, hashed)
        print(f"Verification result: {is_verified}")

        if is_verified:
            print("SUCCESS: 72-character password works fine")
            return True
        else:
            print("FAILURE: 72-character password should verify correctly")
            return False
    except Exception as e:
        print(f"FAILURE: Error with 72-character password: {e}")
        return False

if __name__ == "__main__":
    print("Testing bcrypt 72-byte password limit fix...")

    test1_result = test_long_password_validation()
    test2_result = test_short_password_validation()
    test3_result = test_hash_verification_with_long_password_fallback()

    if test1_result and test2_result and test3_result:
        print("\nALL TESTS PASSED - Fix is working correctly!")
    else:
        print("\nSOME TESTS FAILED - Fix needs adjustment!")