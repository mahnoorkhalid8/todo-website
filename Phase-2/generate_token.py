import os
import sys
from datetime import datetime, timedelta
from jose import jwt

# Load environment variables from the .env file
from dotenv import load_dotenv
load_dotenv()

# Get the actual secret key from environment
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", os.getenv("JWT_SECRET", "fallback-secret-key"))
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a new access token with the provided data.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)  # Default 30 minutes

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Example: Generate a token for a test user
user_data = {
    "sub": "test-user-id-123",
    "email": "test@example.com",
    "name": "Test User"
}

# Create token with 30-minute expiration
token = create_access_token(user_data, timedelta(minutes=30))

print("Generated JWT Token:")
print("="*50)
print(token)
print("="*50)
print(f"\nToken details:")
print(f"- Expires in: 30 minutes")
print(f"- Generated at: {datetime.utcnow().isoformat()}")
print(f"- Will expire at: {(datetime.utcnow() + timedelta(minutes=30)).isoformat()} UTC")

# Verify the token can be decoded
try:
    decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(f"\nSUCCESS: Token verification successful!")
    print(f"Decoded payload: {decoded_payload}")
except Exception as e:
    print(f"\nERROR: Token verification failed: {e}")