from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta
from sqlmodel import Session
import os

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a new access token
    """
    # Import inside the function to avoid early initialization
    try:
        # Try relative imports first (works when running as a package)
        from ..config import settings
    except (ImportError, ValueError):
        # Fall back to absolute imports (works when running directly)
        from config import settings

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current user from JWT token
    """
    # Import inside the function to avoid early initialization
    try:
        # Try relative imports first (works when running as a package)
        from .database import get_db_session
        from ..models import User
        from ..schemas.auth import TokenData, UserResponse
        from ..config import settings
    except (ImportError, ValueError):
        # Fall back to absolute imports (works when running directly)
        from dependencies.database import get_db_session
        from models import User
        from schemas.auth import TokenData, UserResponse
        from config import settings

    # Get a database session manually since we can't use Depends in this context
    session_gen = get_db_session()
    session = next(session_gen)  # Get the session

    try:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
            token_data = TokenData(user_id=user_id, email=payload.get("email"))
        except JWTError:
            raise credentials_exception

        user = session.get(User, token_data.user_id)
        if user is None:
            raise credentials_exception

        # Extract the user data before the session closes to avoid DetachedInstanceError
        user_data = UserResponse(id=user.id, email=user.email, name=user.name)
        return user_data
    finally:
        # Close the session properly
        try:
            next(session_gen)
        except StopIteration:
            pass  # Generator exhausted, session closed


def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Get current active user (can be extended for additional checks)
    """
    # The user is already a UserResponse object, so just return it
    return current_user


# Apply type annotations after imports are resolved
try:
    from ..schemas.auth import TokenData, UserResponse
    from .database import get_db_session
    from ..config import settings
    from ..models import User

    # Update function annotations
    create_access_token.__annotations__ = {
        'data': dict,
        'expires_delta': Optional[timedelta],
        'return': str
    }

    get_current_user.__annotations__ = {
        'credentials': HTTPAuthorizationCredentials,
        'return': UserResponse
    }

    get_current_active_user.__annotations__ = {
        'current_user': UserResponse,
        'return': UserResponse
    }
except:
    # If type annotation fails, continue without it
    pass