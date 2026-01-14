"""
Test configuration and fixtures for the Todo application backend tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from sqlmodel.pool import StaticPool
from datetime import datetime, timedelta
from jose import jwt
import os
from unittest.mock import patch, MagicMock
# Import FastAPI app directly from main module
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
from models import Task


# Create an in-memory SQLite database for testing
@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a database session for testing."""
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="real_token_payload")
def real_token_payload_fixture():
    """Real JWT token payload using actual secret from environment."""
    return {
        "user_id": "test-user-id",
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),  # Expires in 1 hour
        "sub": "test-user-id"
    }


@pytest.fixture(name="real_jwt_token")
def real_jwt_token_fixture(real_token_payload):
    """Create a real JWT token using the actual secret from environment."""
    # Get the secret from environment or fall back to settings
    secret = os.getenv("BETTER_AUTH_SECRET") or getattr(__import__('config').settings, 'better_auth_secret', 'fallback-secret-for-tests')
    return jwt.encode(real_token_payload, secret, algorithm="HS256")


@pytest.fixture(name="client")
def client_fixture():
    """Create a test client."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(name="valid_token_headers")
def valid_token_headers_fixture(real_jwt_token):
    """Headers with a real JWT token using actual secret."""
    return {"Authorization": f"Bearer {real_jwt_token}"}


@pytest.fixture(name="invalid_token_headers")
def invalid_token_headers_fixture():
    """Headers with an invalid JWT token."""
    # Create an invalid token by using a wrong secret
    invalid_payload = {
        "user_id": "test-user-id",
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "sub": "test-user-id"
    }
    invalid_token = jwt.encode(invalid_payload, "wrong-secret", algorithm="HS256")
    return {"Authorization": f"Bearer {invalid_token}"}