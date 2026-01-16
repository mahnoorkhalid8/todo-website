from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import bcrypt

# Handle imports for both local development and Hugging Face deployment
try:
    # Try relative import first (works when running as a package)
    from ..config import settings
except (ImportError, ValueError):
    # Fall back to absolute import (works when running directly)
    from config import settings


# Simple password hashing using bcrypt directly to avoid backend initialization issues
import bcrypt

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt directly
    Truncate password to 72 bytes if longer to avoid bcrypt limitations
    """
    # Bcrypt has a 72 byte password length limit
    # Truncate the password to avoid ValueError
    truncated_password = password[:72] if len(password) > 72 else password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(truncated_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password using bcrypt directly
    Truncate password to 72 bytes if longer to avoid bcrypt limitations
    """
    # Bcrypt has a 72 byte password length limit
    # Truncate the password to avoid ValueError
    truncated_password = plain_password[:72] if len(plain_password) > 72 else plain_password
    try:
        return bcrypt.checkpw(truncated_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        # If verification fails for any reason, return False
        return False

# Define pwd_context as a dummy to avoid errors in existing code
class DummyPwdContext:
    def hash(self, password):
        return get_password_hash(password)

    def verify(self, password, hashed):
        return verify_password(password, hashed)

pwd_context = DummyPwdContext()






def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a new access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify a JWT token and return the payload
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


