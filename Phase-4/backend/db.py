from sqlmodel import create_engine, Session, SQLModel
from contextlib import contextmanager
from typing import Generator
import os
from models import User, Task  # Import all models to register them with SQLModel

# Get database URL from environment, with Neon database as default
# If DATABASE_URL is not set, construct it from individual components
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Construct DATABASE_URL from individual environment variables
    db_host = os.getenv("DATABASE_HOST", "localhost")
    db_port = os.getenv("DATABASE_PORT", "5432")
    db_name = os.getenv("DATABASE_NAME", "todo_chatbot")
    db_user = os.getenv("DATABASE_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "")

    if db_password:
        DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        # Fallback to Neon database if no password provided
        DATABASE_URL = "postgresql://neondb_owner:npg_1wiNqRWc4MPh@ep-sparkling-term-a4onppqn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Create the engine with connection pooling settings
# Handle both PostgreSQL and SQLite engines appropriately
try:
    if DATABASE_URL.startswith("postgresql"):
        # PostgreSQL engine for Neon - with Neon-compatible connection settings
        engine = create_engine(
            DATABASE_URL,
            echo=False,  # Set to True to see SQL queries in logs
            pool_pre_ping=True,        # Verify connections before use
            pool_recycle=300,          # Recycle connections every 5 minutes
            pool_timeout=20,           # Time to wait for connection
            max_overflow=0,            # Limit overflow connections for Neon
            pool_size=5,               # Connection pool size
            connect_args={
                "connect_timeout": 10,   # Connection timeout (valid for psycopg2)
                "keepalives_idle": 10,
                "keepalives_interval": 5,
                "keepalives_count": 2
            }
        )
    else:
        # SQLite engine as fallback
        engine = create_engine(
            DATABASE_URL,
            echo=False,  # Set to True to see SQL queries in logs
            connect_args={"check_same_thread": False}  # Needed for SQLite with FastAPI
        )
    print(f"Connected to database: {DATABASE_URL[:50]}...")  # Show connection info
except Exception as e:
    print(f"Database engine creation failed: {e}")
    print("Switching to local SQLite database as fallback...")
    # Fallback to SQLite
    DATABASE_URL = "sqlite:///./todo_app_local.db"
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
    print(f"Fallback to local SQLite database: {DATABASE_URL}")


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