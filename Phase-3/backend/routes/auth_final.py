from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from datetime import timedelta

# Initialize router first
router = APIRouter()

# Define routes with string annotations to avoid import issues at definition time
@router.post("/register")
def register(user: "UserCreate", session: Session = Depends(lambda: None)):
    # Import everything inside the function to avoid early initialization issues
    try:
        # Try relative imports first (works when running as a package)
        from ..schemas.auth import UserCreate, Token, UserResponse
        from ..utils.auth import create_access_token
        from ..services.auth_service import create_user
        from ..utils.validation import validate_email
        from ..db import get_session
    except ImportError:
        # Fall back to absolute imports (works when running directly)
        import sys
        import os
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)

        from schemas.auth import UserCreate, Token, UserResponse
        from utils.auth import create_access_token
        from services.auth_service import create_user
        from utils.validation import validate_email
        from db import get_session

    # Get the actual database session
    with get_session() as actual_session:
        session = actual_session

        # Validate email format
        validated_user = UserCreate(**user if isinstance(user, dict) else user.__dict__ if hasattr(user, '__dict__') else user)
        if not validate_email(validated_user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )

        # Create user using the service
        print(f"About to call create_user with email: {validated_user.email}")
        db_user = create_user(session, validated_user.email, validated_user.password, validated_user.name)
        print(f"Created user: {db_user}")

        # Create access token for the new user
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": db_user.id, "email": db_user.email},
            expires_delta=access_token_expires
        )
        print(f"Created access token: {access_token[:20]}...")

        # Return token and user info
        user_response = UserResponse(
            id=str(db_user.id),
            email=db_user.email,
            name=db_user.name
        )
        print(f"Created user response: {user_response}")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }


@router.post("/login")
def login(user_credentials: "UserLogin", session: Session = Depends(lambda: None)):
    # Import everything inside the function to avoid early initialization issues
    try:
        # Try relative imports first (works when running as a package)
        from ..schemas.auth import UserLogin, Token, UserResponse
        from ..utils.auth import create_access_token
        from ..services.auth_service import authenticate_user
        from ..db import get_session
    except ImportError:
        # Fall back to absolute imports (works when running directly)
        import sys
        import os
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)

        from schemas.auth import UserLogin, Token, UserResponse
        from utils.auth import create_access_token
        from services.auth_service import authenticate_user
        from db import get_session

    # Get the actual database session
    with get_session() as actual_session:
        session = actual_session

    user = authenticate_user(session, user_credentials.email, user_credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )

    # Create user response
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }


@router.post("/logout")
def logout():
    return {"success": True, "message": "Logged out successfully"}


# Apply proper type annotations after imports are available to fix the OpenAPI schema
try:
    from ..schemas.auth import UserCreate, UserLogin, Token
    from ..dependencies.database import get_db_session

    # Update the route definitions to have proper response models
    # This updates the route after the fact to fix the OpenAPI schema
    for route in router.routes:
        if route.path == "/register":
            route.dependant.call = register
            route.response_model = Token
        elif route.path == "/login":
            route.dependant.call = login
            route.response_model = Token
except:
    # If we can't update the route definitions, continue with original setup
    pass