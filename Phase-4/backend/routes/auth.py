from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session
from datetime import timedelta
import sys
import os

# Add the backend directory to the path to handle different import scenarios
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import schemas and functions with multiple fallback strategies
def safe_import_auth_components():
    global UserCreate, UserLogin, Token, UserResponse, get_db_session, create_access_token
    global create_user, authenticate_user, validate_email, validate_password

    try:
        # Try relative imports first (works when running as a package)
        from ..schemas.auth import UserCreate, UserLogin, Token, UserResponse
        from ..dependencies.database import get_db_session
        from ..utils.auth import create_access_token
        from ..services.auth_service import create_user, authenticate_user
        from ..utils.validation import validate_email, validate_password
        from ..models import User
        print("DEBUG: All auth components imported successfully via relative imports")
        return True
    except (ImportError, ValueError) as e:
        print(f"DEBUG: Relative import failed: {e}")
        try:
            # Fall back to absolute imports (works when running directly or in container)
            from schemas.auth import UserCreate, UserLogin, Token, UserResponse
            from dependencies.database import get_db_session
            from utils.auth import create_access_token
            from services.auth_service import create_user, authenticate_user
            from utils.validation import validate_email, validate_password
            from models import User
            print("DEBUG: All auth components imported successfully via absolute imports")
            return True
        except ImportError as e:
            print(f"DEBUG: Absolute import failed: {e}")
            # Define fallback classes and functions
            from pydantic import BaseModel
            from typing import Optional
            from fastapi import Depends

            class UserCreate(BaseModel):
                name: str
                email: str
                password: str

            class UserLogin(BaseModel):
                email: str
                password: str

            class Token(BaseModel):
                access_token: str
                token_type: str

            class UserResponse(BaseModel):
                id: str
                email: str
                name: str

            def get_db_session():
                yield None

            def create_access_token(data, expires_delta=None):
                return "placeholder_token"

            def create_user(session, email, password, name):
                print("ERROR: create_user service not available")
                return None

            def authenticate_user(session, email, password):
                print("ERROR: authenticate_user service not available")
                return None

            def validate_email(email):
                return "@" in email and "." in email

            def validate_password(password):
                return len(password) >= 8

            print("DEBUG: Fallback auth components defined")
            return True

# Call the import function to set up components
safe_import_auth_components()

router = APIRouter()


@router.post("/register", response_model=Token)
async def register(user: UserCreate = Body(...), session: Session = Depends(get_db_session)):
    # Validate email format
    if not validate_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    try:
        # Create user using the service
        print(f"About to call create_user with email: {user.email}")
        db_user = create_user(session, user.email, user.password, user.name)
        print(f"Created user: {db_user}")

        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user - service unavailable"
            )

        # Create access token for the new user
        access_token_expires = timedelta(minutes=30)  # Use appropriate expiration
        access_token = create_access_token(
            data={"sub": db_user.id, "email": db_user.email},
            expires_delta=access_token_expires
        )
        print(f"Created access token: {access_token[:20]}...")

        # Return token and user info
        user_response = UserResponse(
            id=str(db_user.id),  # Convert to string to ensure compatibility
            email=db_user.email,
            name=db_user.name
        )
        print(f"Created user response: {user_response}")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
    except ValueError as e:
        print(f"ValueError in register: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"General error in register: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin = Body(...), session: Session = Depends(get_db_session)):
    user = authenticate_user(session, user_credentials.email, user_credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=30)  # Use appropriate expiration
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )

    # Create user response with proper handling of optional name
    try:
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name
        )
    except Exception as e:
        print(f"Error creating UserResponse: {e}")
        user_response = None

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }


@router.post("/logout")
def logout():
    # In a stateless JWT system, logout is typically handled on the client side
    # This endpoint could be used for additional server-side operations if needed
    return {"success": True, "message": "Logged out successfully"}