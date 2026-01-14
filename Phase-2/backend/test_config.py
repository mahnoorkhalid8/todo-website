import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can access the .env file
parent_dir = Path(__file__).parent.parent
env_file = parent_dir / '.env'

# Read the .env file manually
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# Print the DATABASE_URL to verify it
db_url = os.getenv('DATABASE_URL')
print(f"DATABASE_URL from environment: {db_url}")

# Check if BETTER_AUTH_SECRET is loaded
auth_secret = os.getenv('BETTER_AUTH_SECRET')
print(f"BETTER_AUTH_SECRET loaded: {'Yes' if auth_secret else 'No'}")
print(f"BETTER_AUTH_SECRET length: {len(auth_secret) if auth_secret else 0}")

# Test JWT token generation with environment secret
from jose import jwt
from datetime import datetime, timedelta

if auth_secret:
    payload = {
        "user_id": "test-user-id",
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "sub": "test-user-id"
    }

    token = jwt.encode(payload, auth_secret, algorithm="HS256")
    print(f"JWT token generated successfully: {token[:50]}...")

    # Verify the token
    try:
        decoded = jwt.decode(token, auth_secret, algorithms=["HS256"])
        print(f"Token verification successful. User ID: {decoded.get('user_id')}")
    except Exception as e:
        print(f"Token verification failed: {e}")
else:
    print("Could not generate JWT token - no auth secret found")