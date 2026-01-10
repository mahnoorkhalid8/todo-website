from sqlmodel import create_engine, Session, SQLModel
from contextlib import contextmanager
from typing import Generator
import os

# Import models to register them with SQLModel
# Handle imports for both local development and Hugging Face deployment
try:
    # Try relative import first (works when running as a package)
    from . import models  # Import the models module to register all models with SQLModel
except ImportError:
    # Fall back to absolute import (works when running directly)
    import models  # Import the models module to register all models with SQLModel


def get_engine():
    """Get database engine with proper environment variable handling"""
    # Import settings to use the same configuration as config.py
    # Try multiple import strategies to handle different execution contexts
    DATABASE_URL = None

    # First try relative import (for when running as package)
    try:
        from .config import settings
        DATABASE_URL = settings.DATABASE_URL
    except (ImportError, AttributeError):
        # Try absolute import (for when running directly)
        try:
            from config import settings
            DATABASE_URL = settings.DATABASE_URL
        except (ImportError, AttributeError):
            # Fallback to environment variable if config import fails
            DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/todo_app")

    # Adjust connection parameters for remote databases like Neon
    if "neon.tech" in DATABASE_URL:
        # Special configuration for Neon database
        return create_engine(
            DATABASE_URL,
            echo=False,  # Set to True to see SQL queries in logs
            pool_pre_ping=True,
            pool_size=2,  # Smaller pool for remote connections
            max_overflow=5,  # Reduced overflow
            pool_recycle=300,  # Recycle connections every 5 minutes
            pool_timeout=30,  # 30 seconds timeout
            pool_reset_on_return='commit',
            connect_args={
                "connect_timeout": 15,  # 15 second connection timeout
                "keepalives_idle": 600,
                "keepalives_interval": 30,
                "keepalives_count": 3,
                "sslmode": "require",
            }
        )
    else:
        # Standard configuration for local databases
        return create_engine(
            DATABASE_URL,
            echo=False,  # Set to True to see SQL queries in logs
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_recycle=300,
        )


def create_db_and_tables():
    """
    Create database tables if they don't exist
    This should be called on application startup
    """
    # Create engine dynamically to respect current environment
    engine = get_engine()
    # Ensure models are imported to register with SQLModel
    try:
        from . import models
    except ImportError:
        import models
    SQLModel.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions
    Ensures proper cleanup of resources
    """
    engine = get_engine()  # Use dynamic engine to respect environment
    session = Session(engine)
    try:
        yield session
        # Commit all changes at the end of the context
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session_override():
    """
    Dependency override for testing
    """
    yield get_session()