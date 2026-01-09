from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from datetime import timedelta
# Handle imports for both local development and Hugging Face deployment
try:
    # Try relative imports first (works when running as a package)
    from ..dependencies.database import get_db_session
    from ..models import User
    from ..schemas.auth import UserCreate, UserLogin, Token, UserResponse
    from ..utils.auth import create_access_token
    from ..services.auth_service import create_user, authenticate_user
    from ..utils.validation import validate_email, validate_password
except (ImportError, ValueError):
    # Fall back to absolute imports (works when running directly)
    from dependencies.database import get_db_session
    from models import User
    from schemas.auth import UserCreate, UserLogin, Token, UserResponse
    from utils.auth import create_access_token
    from services.auth_service import create_user, authenticate_user
    from utils.validation import validate_email, validate_password


router = APIRouter()


@router.post("/register", response_model=Token)
def register(user: UserCreate, session: Session = Depends(get_db_session)):
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
def login(user_credentials: UserLogin, session: Session = Depends(get_db_session)):
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
    # Try to create the UserResponse and handle potential errors
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