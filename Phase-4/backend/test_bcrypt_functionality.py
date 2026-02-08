#!/usr/bin/env python3
"""
Test script to verify bcrypt functionality works properly after fixes
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_bcrypt_functionality():
    """Test that bcrypt functionality works properly"""
    print("Testing bcrypt functionality after fixes...")

    try:
        # Import the auth utilities
        from utils.auth import get_password_hash, verify_password

        print("✅ Successfully imported auth utilities")

        # Test password hashing
        test_password = "TestPass123!"
        print(f"Testing with password: {test_password}")

        # Hash the password
        hashed = get_password_hash(test_password)
        print(f"✅ Password hashed successfully: {hashed[:20]}...")

        # Verify the password
        is_valid = verify_password(test_password, hashed)
        print(f"✅ Password verification result: {is_valid}")

        if is_valid:
            print("✅ Password hashing and verification working correctly!")
        else:
            print("❌ Password verification failed!")
            return False

        # Test with wrong password
        is_invalid = verify_password("WrongPassword123!", hashed)
        print(f"✅ Wrong password verification result: {is_invalid}")

        if not is_invalid:
            print("✅ Correctly rejected wrong password!")
        else:
            print("❌ Failed to reject wrong password!")
            return False

        # Test with 72+ character password (should be truncated)
        long_password = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz123456789!@#$%^&*()AA"  # 73 chars
        print(f"Testing with long password ({len(long_password)} chars)...")

        long_hashed = get_password_hash(long_password)
        print(f"✅ Long password hashed successfully: {long_hashed[:20]}...")

        # Verify with the original long password
        long_valid = verify_password(long_password, long_hashed)
        print(f"✅ Long password verification result: {long_valid}")

        if long_valid:
            print("✅ Long password handling working correctly!")
        else:
            print("❌ Long password verification failed!")
            return False

        return True

    except Exception as e:
        print(f"❌ Error during bcrypt functionality test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bcrypt_functionality()
    if success:
        print("\n🎉 All bcrypt functionality tests passed!")
    else:
        print("\n💥 Bcrypt functionality tests failed!")