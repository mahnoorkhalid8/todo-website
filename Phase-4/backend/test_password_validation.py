#!/usr/bin/env python3
"""
Test script to verify password validation for 'strinG1#'
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from utils.validation import validate_password

def test_password():
    """Test the specific password 'strinG1#'"""
    password = "strinG1#"
    print(f"Testing password: '{password}'")
    print(f"Password length: {len(password)}")

    # Check each validation requirement manually
    print(f"Length >= 8: {len(password) >= 8}")
    print(f"Has uppercase: {any(c.isupper() for c in password)}")
    print(f"Has lowercase: {any(c.islower() for c in password)}")
    print(f"Has digit: {any(c.isdigit() for c in password)}")
    print(f"Has special char: {any(c in '!@#$%^&*(),.?\":{}|<>' for c in password)}")

    is_valid, error_msg = validate_password(password)
    print(f"Validation result: {is_valid}")
    print(f"Error message: {error_msg}")

    if is_valid:
        print("Password is valid!")
    else:
        print("Password is invalid!")

if __name__ == "__main__":
    test_password()