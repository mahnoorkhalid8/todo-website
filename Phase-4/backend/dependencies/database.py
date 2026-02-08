from fastapi import Depends
from sqlmodel import Session

def get_db_session():
    """
    Dependency to get database session
    """
    # Import inside the function to avoid early initialization
    try:
        # Try relative import first (works when running as a package)
        from ..db import get_session as get_db_session_func
    except (ImportError, ValueError):
        # Fall back to absolute import (works when running directly)
        from db import get_session as get_db_session_func

    with get_db_session_func() as session:
        yield session