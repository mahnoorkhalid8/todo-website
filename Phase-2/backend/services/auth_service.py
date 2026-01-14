from sqlmodel import Session, select


def create_user(session: Session, email: str, password: str, name: str):
    """
    Create a new user with validated email and password
    """
    # Import inside the function to avoid early initialization
    try:
        # Try relative imports first (works when running as a package)
        from ..models import User
        from ..utils.auth import verify_password, get_password_hash
        from ..utils.validation import validate_email, validate_password
    except (ImportError, ValueError):
        # Fall back to absolute imports (works when running directly)
        from models import User
        from utils.auth import verify_password, get_password_hash
        from utils.validation import validate_email, validate_password

    # Validate email format
    if not validate_email(email):
        raise ValueError("Invalid email format")

    # Validate password strength
    if not validate_password(password):
        raise ValueError("Password does not meet requirements")

    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        raise ValueError("Email already registered")

    # Hash password
    hashed_password = get_password_hash(password)

    # Create new user
    user = User(
        email=email,
        password_hash=hashed_password,
        name=name
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def authenticate_user(session: Session, email: str, password: str):
    """
    Authenticate user by email and password
    """
    # Import inside the function to avoid early initialization
    try:
        # Try relative imports first (works when running as a package)
        from ..models import User
        from ..utils.auth import verify_password, get_password_hash
    except (ImportError, ValueError):
        # Fall back to absolute imports (works when running directly)
        from models import User
        from utils.auth import verify_password, get_password_hash

    # Find user by email
    user = session.exec(select(User).where(User.email == email)).first()

    # Verify password if user exists
    if user and verify_password(password, user.password_hash):
        return user

    return None


def get_user_by_email(session: Session, email: str):
    """
    Get user by email
    """
    # Import inside the function to avoid early initialization
    try:
        # Try relative imports first (works when running as a package)
        from ..models import User
    except (ImportError, ValueError):
        # Fall back to absolute imports (works when running directly)
        from models import User

    user = session.exec(select(User).where(User.email == email)).first()
    return user


# Apply type annotations after imports are resolved
try:
    from ..models import User
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        # Only for type checking purposes
        def create_user(session: Session, email: str, password: str, name: str = None) -> User:
            pass

        def authenticate_user(session: Session, email: str, password: str) -> User | None:
            pass

        def get_user_by_email(session: Session, email: str) -> User | None:
            pass
except:
    pass