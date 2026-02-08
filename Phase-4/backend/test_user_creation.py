import os
import sys
from sqlalchemy import text

# Set environment variables
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_1wiNqRWc4MPh@ep-sparkling-term-a4onppqn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'
os.environ['SECRET_KEY'] = 'o2nmkwIUqotG5dDCWR0a0rk2Uk2rL0DPBvqbdkwZ54N'

def test_user_creation():
    try:
        # Import the necessary modules
        from db import get_session
        from models import User
        from utils.auth import get_password_hash
        from utils.validation import validate_email, validate_password

        print("Modules imported successfully")

        # Test the validation functions
        print("Validating email...")
        email_valid = validate_email("testuser@example.com")
        print(f"Email validation result: {email_valid}")

        print("Validating password...")
        password_valid, msg = validate_password("Testpassword123!")
        print(f"Password validation result: {password_valid}, message: {msg}")

        # Test database transaction
        print("Testing database transaction...")
        with get_session() as session:
            print("Session created successfully")

            # Check if user already exists
            existing_user = session.query(User).filter(User.email == "testuser@example.com").first()
            if existing_user:
                print("User already exists, deleting for test...")
                session.delete(existing_user)
                session.commit()

            # Hash the password
            hashed_password = get_password_hash("Testpassword123!")
            print(f"Password hashed successfully: {hashed_password[:20]}...")

            # Create new user
            db_user = User(
                email="testuser@example.com",
                name="Test User",
                password_hash=hashed_password
            )

            print("Adding user to session...")
            session.add(db_user)

            print("Committing transaction...")
            session.commit()
            print("Transaction committed successfully!")

            # Refresh to get the ID
            session.refresh(db_user)
            print(f"User created with ID: {db_user.id}")

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_creation()