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

print(f"Using database URL: {DATABASE_URL}")

# Create engine and test connection
try:
    engine = create_engine(DATABASE_URL)
    print("[OK] Successfully connected to database")

    # Test the connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()
        print(f"[OK] Database version: {version[0]}")

    # Import the User model and check for users
    import sys
    sys.path.insert(0, 'backend')

    from backend.models import User

    # Create a session and query users
    with Session(engine) as session:
        statement = select(User)
        users = session.exec(statement).all()

        print(f"\nFound {len(users)} user(s) in the database:")

        for user in users:
            print(f"- ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Name: {user.name}")
            print(f"  Created: {user.created_at}")
            print()

        if len(users) == 0:
            print("No users found in the database.")

except Exception as e:
    print(f"Error connecting to database: {e}")