from sqlmodel import Session

# Handle imports for both local development and Hugging Face deployment
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


def create_user(session: Session, email: str, password: str, name: str = None) -> User:
    """
    Create a new user with validated email and password
    """
    # Validate email format
    if not validate_email(email):
        raise ValueError("Invalid email format")

    # Validate password complexity
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        raise ValueError(error_msg)

    # Check if user already exists
    existing_user = session.query(User).filter(User.email == email).first()
    if existing_user:
        raise ValueError("Email already registered")

    # Hash the password
    hashed_password = get_password_hash(password)

    # Create new user
    db_user = User(
        email=email,
        name=name,
        password_hash=hashed_password
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    """
    Authenticate user with email and password
    """
    user = session.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None

    # Ensure the user object is fully loaded for serialization
    # Access the attributes to ensure they're loaded from the database
    _ = user.id, user.email, user.name  # Force loading of these attributes

    return user


def get_user_by_email(session: Session, email: str) -> User | None:
    """
    Get user by email
    """
    return session.query(User).filter(User.email == email).first()


def get_user_by_id(session: Session, user_id: str) -> User | None:
    """
    Get user by ID
    """
    return session.get(User, user_id)