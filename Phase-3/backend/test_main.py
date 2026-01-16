"""
Basic tests for the Todo API application.
"""
import pytest
from fastapi.testclient import TestClient
from .main import app


def test_read_root():
    """
    Test the root endpoint.
    """
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Todo API is running"}


if __name__ == "__main__":
    test_read_root()
    print("All tests passed!")