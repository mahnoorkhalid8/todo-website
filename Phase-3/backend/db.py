from sqlmodel import create_engine, Session, SQLModel
from contextlib import contextmanager
from typing import Generator
import os

# Handle imports for both local development and Hugging Face deployment
try:
    # Try relative import first (works when running as a package)
    from .models import User, Task  # Import all models to register them with SQLModel
except ImportError:
    # Fall back to absolute import (works when running directly)
    from models import User, Task  # Import all models to register them with SQLModel

# Get database URL from environment, default to a local PostgreSQL database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/todo_app")

# Create the engine with connection pooling settings
engine = create_engine(
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
    SQLModel.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions
    Ensures proper cleanup of resources
    """
    session = Session(engine)
    try:
        yield session
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