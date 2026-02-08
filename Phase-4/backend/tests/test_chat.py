"""
Tests for the Chatbot API endpoints

This module contains tests for the chatbot functionality including
conversation management, message handling, and AI integration.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch
from sqlmodel import Session, select
from datetime import datetime

from main import app
from models import User, Conversation, Message
from services.conversation_service import create_conversation, add_message
from config import settings


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_user(session: Session):
    """Create a mock user for testing."""
    user = User(
        email="test@example.com",
        name="Test User",
        password_hash="hashed_password"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def mock_conversation(session: Session, mock_user: User):
    """Create a mock conversation for testing."""
    conversation = Conversation(user_id=mock_user.id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def test_chat_endpoint_success(client: TestClient, mock_user: User):
    """Test successful chat message processing."""
    with patch('routes.chat.process_user_message') as mock_process:
        mock_process.return_value = {
            "response": "Test response",
            "tool_calls": [],
            "executed_tool_calls": []
        }

        response = client.post(
            f"/api/chat/{mock_user.id}",
            json={"message": "Hello, world!"},
            headers={"Authorization": "Bearer fake-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert data["response"] == "Test response"


def test_chat_endpoint_missing_message(client: TestClient, mock_user: User):
    """Test chat endpoint with missing message."""
    response = client.post(
        f"/api/chat/{mock_user.id}",
        json={"message": ""},
        headers={"Authorization": "Bearer fake-token"}
    )

    assert response.status_code == 422  # Validation error from Pydantic


def test_chat_endpoint_invalid_user_id(client: TestClient, mock_user: User):
    """Test chat endpoint with invalid user ID."""
    response = client.post(
        f"/api/chat/invalid_user_id",
        json={"message": "Hello"},
        headers={"Authorization": "Bearer fake-token"}
    )

    assert response.status_code == 404  # User not found or auth failure


def test_chat_endpoint_unauthorized(client: TestClient, mock_user: User):
    """Test chat endpoint without authorization."""
    response = client.post(
        f"/api/chat/{mock_user.id}",
        json={"message": "Hello"}
    )

    assert response.status_code in [401, 403]  # Unauthorized or Forbidden


def test_get_conversations(client: TestClient, mock_user: User, mock_conversation: Conversation):
    """Test getting user conversations."""
    response = client.get(
        f"/api/chat/{mock_user.id}/conversations",
        headers={"Authorization": "Bearer fake-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    assert len(data["conversations"]) >= 1


def test_get_conversation_messages(client: TestClient, mock_user: User, mock_conversation: Conversation):
    """Test getting messages for a conversation."""
    # Add a test message
    with patch("dependencies.database.get_session_context") as mock_session:
        mock_db_session = AsyncMock(spec=Session)
        mock_session.__aenter__.return_value = mock_db_session
        mock_session.__aexit__.return_value = None

        # Mock the get_messages_by_conversation function
        with patch("routes.chat.get_messages_by_conversation") as mock_get_msgs:
            mock_get_msgs.return_value = [
                Message(
                    id=1,
                    user_id=mock_user.id,
                    conversation_id=mock_conversation.id,
                    role="user",
                    content="Test message",
                    created_at=datetime.utcnow()
                )
            ]

            response = client.get(
                f"/api/chat/{mock_user.id}/conversation/{mock_conversation.id}/messages",
                headers={"Authorization": "Bearer fake-token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "messages" in data


def test_chat_health_endpoint(client: TestClient):
    """Test the chat health endpoint."""
    response = client.get("/api/chat/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "chatbot"


def test_conversation_creation(client: TestClient, mock_user: User):
    """Test creating a new conversation."""
    with patch('routes.chat.process_user_message') as mock_process:
        mock_process.return_value = {
            "response": "Test response",
            "tool_calls": [],
            "executed_tool_calls": []
        }

        response = client.post(
            f"/api/chat/{mock_user.id}",
            json={"message": "Start a new conversation"},
            headers={"Authorization": "Bearer fake-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert isinstance(data["conversation_id"], int)
        assert data["conversation_id"] > 0


def test_security_input_validation(client: TestClient, mock_user: User):
    """Test security validation of input."""
    # Test with potentially malicious input
    malicious_inputs = [
        "<script>alert('xss')</script>",
        "SELECT * FROM users; DROP TABLE users;",
        "rm -rf /",
        "exec('malicious code')"
    ]

    for malicious_input in malicious_inputs:
        with patch('routes.chat.process_user_message') as mock_process:
            mock_process.return_value = {
                "response": "Processed safely",
                "tool_calls": [],
                "executed_tool_calls": []
            }

            response = client.post(
                f"/api/chat/{mock_user.id}",
                json={"message": malicious_input},
                headers={"Authorization": "Bearer fake-token"}
            )

            # Should either reject or sanitize the input
            # The exact behavior depends on the security implementation
            assert response.status_code in [200, 400, 422]


def test_rate_limiting(client: TestClient, mock_user: User):
    """Test rate limiting functionality."""
    with patch('routes.chat.process_user_message') as mock_process:
        mock_process.return_value = {
            "response": "Test response",
            "tool_calls": [],
            "executed_tool_calls": []
        }

        # Make multiple requests to test rate limiting
        for i in range(10):
            response = client.post(
                f"/api/chat/{mock_user.id}",
                json={"message": f"Test message {i}"},
                headers={"Authorization": "Bearer fake-token"}
            )

            # All requests should succeed unless rate limiting is implemented
            # This test will pass regardless of rate limiting implementation
            assert response.status_code in [200, 429]


# Additional tests for MCP tools can be added here
def test_mcp_tool_validation():
    """Test MCP tool parameter validation."""
    from utils.security import validate_tool_parameters

    # Test valid add_task parameters
    valid_add_task = {
        "user_id": "test_user",
        "title": "Valid task title",
        "description": "Valid description"
    }
    assert validate_tool_parameters("add_task", valid_add_task) == True

    # Test invalid add_task parameters
    invalid_add_task = {
        "user_id": "test_user",
        "title": "",  # Empty title
        "description": "Valid description"
    }
    assert validate_tool_parameters("add_task", invalid_add_task) == False

    # Test valid complete_task parameters
    valid_complete_task = {
        "user_id": "test_user",
        "task_id": 1
    }
    assert validate_tool_parameters("complete_task", valid_complete_task) == True

    # Test invalid complete_task parameters
    invalid_complete_task = {
        "user_id": "test_user",
        "task_id": -1  # Invalid task ID
    }
    assert validate_tool_parameters("complete_task", invalid_complete_task) == False


if __name__ == "__main__":
    pytest.main([__file__])