#!/usr/bin/env python3
"""
Final test to confirm registration and login work properly
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def final_test():
    """Final test with valid credentials"""
    print("FINAL TEST: Registration and Login with valid credentials")
    print("="*60)

    # Valid credentials that meet all requirements
    password = "ValidPass123!"  # 13 chars, meets all requirements
    email = "testuser@example.com"  # Valid email
    username = "testuser"

    print(f"Credentials: email={email}, password={password}, username={username}")

    try:
        # Test validation first
        from utils.validation import validate_password, validate_email

        is_valid, error = validate_password(password)
        email_valid = validate_email(email)

        print(f"Password validation: {is_valid} (error: {error})")
        print(f"Email validation: {email_valid}")

        if not is_valid or not email_valid:
            print("❌ Validation failed")
            return False

        print("✅ All validations passed")

        # Test bcrypt functionality
        from utils.auth import get_password_hash, verify_password

        print("Testing bcrypt functionality...")
        hashed = get_password_hash(password)
        print(f"Password hashing: Success (hash starts with: {hashed[:10]})")

        verified = verify_password(password, hashed)
        print(f"Password verification: {verified}")

        if not verified:
            print("❌ Password verification failed")
            return False

        print("✅ Bcrypt functionality working")

        # Test database integration
        print("Testing database integration...")
        from sqlmodel import Session
        from db import get_engine
        from services.auth_service import create_user, authenticate_user

        engine = get_engine()

        with Session(engine) as session:
            # Clean up any existing test user
            from models import User
            existing = session.query(User).filter(User.email == email).first()
            if existing:
                session.delete(existing)
                session.commit()

            # Test registration
            print("Testing registration...")
            user = create_user(session, email, password, username)
            session.commit()
            print(f"Registration: Success (user ID: {user.id})")

            # Test login
            print("Testing login...")
            authenticated = authenticate_user(session, email, password)
            if authenticated:
                print(f"Login: Success (user ID: {authenticated.id})")
            else:
                print("Login: Failed")
                return False

        print("✅ Database integration working")

        print("\n🎉 ALL TESTS PASSED!")
        print("The authentication system is working correctly.")
        print("\nNote: The original password 'Abc1!' failed because it's only 5 characters,")
        print("but the requirements are minimum 8 characters with mixed case, digits, and special chars.")
        print("\nThe system is now stable and working without bcrypt errors.")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = final_test()
    if success:
        print("\n✅ AUTHENTICATION SYSTEM IS WORKING PROPERLY!")
    else:
        print("\n❌ ISSUES FOUND WITH THE AUTHENTICATION SYSTEM")