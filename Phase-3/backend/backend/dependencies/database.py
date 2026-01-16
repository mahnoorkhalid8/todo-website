from fastapi import Depends
from sqlmodel import Session

# Handle imports for both local development and Hugging Face deployment
try:
    # Try relative import first (works when running as a package)
    from ..db import get_session
except (ImportError, ValueError):
    # Fall back to absolute import (works when running directly)
    from db import get_session


def get_db_session():
    """
    Dependency to get database session
    """
    with get_session() as session:
        yield session