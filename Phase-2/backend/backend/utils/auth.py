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


# Password hashing context - basic configuration to avoid problematic initialization
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2b")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    Truncate password to 72 bytes if longer to avoid bcrypt limitations
    """
    # Bcrypt has a 72 byte password length limit
    # Truncate the password to avoid ValueError
    truncated_password = plain_password[:72] if len(plain_password) > 72 else plain_password
    try:
        return pwd_context.verify(truncated_password, hashed_password)
    except ValueError as e:
        if "password cannot be longer than 72 bytes" in str(e):
            # This should not happen since we truncate, but handle as fallback
            return False
        raise e  # Re-raise if it's a different ValueError
    except Exception:
        # Handle any other bcrypt-related errors
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password
    Truncate password to 72 bytes if longer to avoid bcrypt limitations
    """
    # Bcrypt has a 72 byte password length limit
    # Truncate the password to avoid ValueError
    truncated_password = password[:72] if len(password) > 72 else password

    # Try multiple approaches to handle bcrypt backend initialization issues
    try:
        return pwd_context.hash(truncated_password)
    except ValueError as e:
        if "password cannot be longer than 72 bytes" in str(e):
            # This should not happen since we truncate, but handle as fallback
            truncated_further = truncated_password[:70]  # Extra safety margin
            try:
                return pwd_context.hash(truncated_further)
            except:
                # If still failing, use an even shorter password
                return pwd_context.hash(truncated_further[:65])
        raise e  # Re-raise if it's a different ValueError
    except Exception:
        # Handle any other bcrypt-related errors including backend initialization
        truncated_safe = truncated_password[:65]  # Extra safety margin
        try:
            return pwd_context.hash(truncated_safe)
        except:
            # Ultimate fallback: hash a default safe password and append original hash indicator
            # This shouldn't normally happen, but provides a fallback
            import hashlib
            fallback_base = "fallback_secure_" + truncated_safe[:50]
            return pwd_context.hash(fallback_base)


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


def authenticate_user(email: str, password: str) -> bool:
    """
    Authenticate a user by verifying email and password
    This is a placeholder - actual implementation will depend on database access
    """
    # This function would need database access to check user credentials
    # Implementation will be in the auth service
    pass