import asyncio
from sqlalchemy import create_engine, text
from sqlmodel import Session, select
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment variables")
    exit(1)

print(f"Checking database for user: mahnoorkhalid814@gmail.com")

# Create engine and test connection
try:
    engine = create_engine(DATABASE_URL)
    print("[OK] Successfully connected to database")

    # Import the User model and check for the specific user
    import sys
    sys.path.insert(0, 'backend')

    from backend.models import User

    # Create a session and query the specific user
    with Session(engine) as session:
        statement = select(User).where(User.email == "mahnoorkhalid814@gmail.com")
        user = session.exec(statement).first()

        if user:
            print(f"\n[FOUND] User exists in database:")
            print(f"- ID: {user.id}")
            print(f"- Email: {user.email}")
            print(f"- Name: {user.name}")
            print(f"- Created: {user.created_at}")
            print(f"- Updated: {user.updated_at}")
        else:
            print("\n[NOT FOUND] User 'mahnoorkhalid814@gmail.com' not found in database")

            # Let's check all users to confirm the database is working
            all_users = session.exec(select(User)).all()
            print(f"\nTotal users in database: {len(all_users)}")
            print("Sample of users in database:")
            for i, u in enumerate(all_users[:5]):  # Show first 5 users
                print(f"- {u.email} ({u.name})")

except Exception as e:
    print(f"Error connecting to database: {e}")