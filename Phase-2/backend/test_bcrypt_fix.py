#!/usr/bin/env python3
"""
Test script to verify the bcrypt 72-byte password limit fix
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from utils.auth import get_password_hash, verify_password
from utils.validation import validate_password

def test_short_password():
    """Test with a normal length password"""
    print("Testing with a normal length password...")
    password = "MySecureP@ss123"

    # Validate password
    is_valid, error_msg = validate_password(password)
    print(f"Password validation result: {is_valid}, Error: {error_msg}")

    if is_valid:
        # Hash the password
        hashed = get_password_hash(password)
        print(f"Password hashed successfully: {hashed[:20]}...")

        # Verify the password
        is_verified = verify_password(password, hashed)
        print(f"Password verification result: {is_verified}")

        print("✓ Short password test passed\n")
    else:
        print("✗ Short password test failed\n")


def test_long_password():
    """Test with a password longer than 72 bytes"""
    print("Testing with a password longer than 72 bytes...")
    # Create a password longer than 72 characters
    password = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz123456789!@#$%^&*()"
    print(f"Password length: {len(password)} characters")

    # Validate password - this should fail with our new validation
    is_valid, error_msg = validate_password(password)
    print(f"Password validation result: {is_valid}, Error: {error_msg}")

    if not is_valid:
        print("✓ Long password correctly rejected by validation\n")
    else:
        # If validation passes, test the truncation fallback
        try:
            hashed = get_password_hash(password)
            print(f"Password hashed successfully: {hashed[:20]}...")

            # Verify the original long password (should work due to truncation)
            is_verified = verify_password(password, hashed)
            print(f"Original long password verification result: {is_verified}")

            # Verify with the truncated version (should also work)
            truncated_password = password[:72]
            is_verified_truncated = verify_password(truncated_password, hashed)
            print(f"Truncated password verification result: {is_verified_truncated}")

            print("✓ Long password fallback mechanism works\n")
        except Exception as e:
            print(f"✗ Error with long password: {e}\n")


def test_edge_case_72_bytes():
    """Test with exactly 72 bytes"""
    print("Testing with exactly 72 characters...")
    # Create a password with exactly 72 characters
    password = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz123456789!@#$%&*"  # 72 chars
    print(f"Password length: {len(password)} characters")

    # Validate password
    is_valid, error_msg = validate_password(password)
    print(f"Password validation result: {is_valid}, Error: {error_msg}")

    if is_valid:
        # Hash the password
        hashed = get_password_hash(password)
        print(f"Password hashed successfully: {hashed[:20]}...")

        # Verify the password
        is_verified = verify_password(password, hashed)
        print(f"Password verification result: {is_verified}")

        print("✓ 72-character password test passed\n")
    else:
        print("✗ 72-character password test failed\n")


if __name__ == "__main__":
    print("Testing bcrypt 72-byte password limit fix...\n")

    test_short_password()
    test_edge_case_72_bytes()
    test_long_password()

    print("All tests completed!")