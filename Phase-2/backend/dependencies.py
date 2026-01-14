"""
FastAPI dependency injection for the Todo application.
"""
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends, HTTPException, status
from .db import get_async_session
from .auth import get_current_user_id, verify_user_owns_resource


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session dependency.
    """
    async for session in get_async_session():
        yield session


def get_current_user_id_dep():
    """
    Dependency to get the current user ID from the JWT token.
    """
    return Depends(get_current_user_id)


def verify_user_ownership(user_id_from_token: str = Depends(get_current_user_id), user_id_from_url: str = None):
    """
    Dependency to verify that the user owns the resource they're trying to access.
    """
    if user_id_from_url:
        verify_user_owns_resource(user_id_from_token, user_id_from_url)
    return user_id_from_token