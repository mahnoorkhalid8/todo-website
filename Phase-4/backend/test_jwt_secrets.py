#!/usr/bin/env python3
"""
Test script to verify that JWT token generation works with real environment secrets.
"""
import os
import sys
from datetime import datetime, timedelta
from jose import jwt

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Import settings from config
from config import settings

def test_jwt_generation():
    """Test JWT token generation with real environment secrets."""
    print("Testing JWT token generation with real environment secrets...")

    # Create a test payload
    payload = {
        "user_id": "test-user-id",
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),  # Expires in 1 hour
        "sub": "test-user-id"
    }

    print(f"Using BETTER_AUTH_SECRET from environment: {'Yes' if settings.better_auth_secret else 'No'}")
    print(f"Secret length: {len(settings.better_auth_secret) if settings.better_auth_secret else 0}")

    # Generate token using the real secret from settings
    token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")
    print(f"Generated token: {token[:50]}...")  # Print first 50 chars

    # Verify the token can be decoded with the same secret
    try:
        decoded_payload = jwt.decode(token, settings.better_auth_secret, algorithms=["HS256"])
        print("SUCCESS: Token verification successful")
        print(f"Decoded user_id: {decoded_payload.get('user_id')}")
        print(f"Decoded email: {decoded_payload.get('email')}")
        print(f"Token expires at: {datetime.fromtimestamp(decoded_payload.get('exp', 0))}")
        return True
    except Exception as e:
        print(f"FAILED: Token verification failed: {e}")
        return False

if __name__ == "__main__":
    success = test_jwt_generation()
    if success:
        print("\nSUCCESS: Real environment secrets are working correctly!")
    else:
        print("\nFAILED: Real environment secrets are not working correctly!")
        sys.exit(1)