"""
Authentication middleware for the Todo application to handle JWT token verification
and ensure user isolation by validating user access to resources.
"""
import logging
import re
from typing import Optional
from fastapi import Request, HTTPException, status
from jose import JWTError, jwt
from config import settings


logger = logging.getLogger(__name__)


async def verify_token(token: str) -> Optional[dict]:
    """
    Verify a JWT token and return the payload if valid.
    """
    try:
        payload = jwt.decode(token, settings.better_auth_secret, algorithms=["HS256"])
        return payload
    except JWTError as e:
        logger.error(f"JWT token verification failed: {str(e)}")
        return None


async def auth_middleware(request: Request, call_next):
    """
    Authentication middleware to handle JWT token verification and user isolation.
    """
    # Define paths that don't require authentication
    public_paths = ["/", "/docs", "/redoc", "/openapi.json"]

    # Extract the base path without query parameters for comparison
    path = request.url.path
    if path in public_paths:
        response = await call_next(request)
        return response

    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid"
        )

    token = auth_header.split(" ")[1]

    # Verify the token
    payload = await verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # Add user info to request state for downstream handlers
    request.state.user_id = payload.get("user_id")
    request.state.user_info = payload

    # Extract user_id from URL path for validation against token
    # Pattern matches /api/{user_id}/... paths
    path_match = re.match(r"^/api/([^/]+)/", path)
    if path_match:
        url_user_id = path_match.group(1)
        # Validate that the user_id in the token matches the user_id in the URL
        token_user_id = payload.get("user_id")
        if token_user_id and url_user_id and token_user_id != url_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resource"
            )

    response = await call_next(request)
    return response


async def verify_user_access_from_state(request: Request, user_id_from_url: str):
    """
    Verify that the authenticated user can access the requested resource.
    This function checks if the user_id from the token matches the user_id in the URL.
    """
    if hasattr(request.state, 'user_id') and request.state.user_id:
        user_id_from_token = request.state.user_id
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )

    if user_id_from_token != user_id_from_url:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

    return user_id_from_token