"""
Authentication middleware and JWT handling for the Todo application.
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from .config import settings


security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a new access token with the provided data.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)  # Default 30 minutes
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.better_auth_secret, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify a JWT token and return the payload if valid.
    """
    try:
        payload = jwt.decode(token, settings.better_auth_secret, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Get the current user ID from the JWT token in the Authorization header.
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def verify_user_owns_resource(user_id_from_token: str, user_id_from_url: str):
    """
    Verify that the user ID from the token matches the user ID from the URL.
    This ensures users can only access their own resources.
    """
    if user_id_from_token != user_id_from_url:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )