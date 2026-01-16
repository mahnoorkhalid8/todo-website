import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password complexity
    Returns (is_valid, error_message)
    """
    # Check password length - bcrypt has a 72 byte limit
    if len(password) > 72:
        return False, "Password must not exceed 72 characters (bcrypt limitation)"

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"

    return True, None


def validate_task_title(title: str) -> tuple[bool, Optional[str]]:
    """
    Validate task title length
    Returns (is_valid, error_message)
    """
    if not title or len(title) < 1 or len(title) > 200:
        return False, "Task title must be between 1 and 200 characters"

    return True, None


def validate_task_description(description: Optional[str]) -> tuple[bool, Optional[str]]:
    """
    Validate task description length
    Returns (is_valid, error_message)
    """
    if description and len(description) > 1000:
        return False, "Task description must be less than 1000 characters"

    return True, None