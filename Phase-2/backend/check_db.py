import asyncio
from sqlmodel import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from models import User, Task
from config import settings
import os

def test_database_connection():
    """Test database connection and check existing data"""
    print("Testing database connection...")
    print(f"Database URL: {settings.DATABASE_URL.replace('@', '[@]').replace(':', '[:]')[:50]}...")  # Mask sensitive info

    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL, echo=False)

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(select(1))
            print("SUCCESS: Database connection successful!")

        # Count users
        from sqlmodel import Session
        with Session(engine) as session:
            user_result = session.exec(select(User))
            users = user_result.all()
            user_count = len(users)
            print(f"Found {user_count} users in database")

            # Get all users if any exist
            if user_count > 0:
                print("Users in database:")
                for user in users:
                    print(f"  - ID: {user.id}, Email: {user.email}, Name: {user.name}")

            # Count tasks
            task_result = session.exec(select(Task))
            tasks = task_result.all()
            task_count = len(tasks)
            print(f"Found {task_count} tasks in database")

            # Get all tasks if any exist
            if task_count > 0:
                print("Tasks in database:")
                for task in tasks:
                    print(f"  - ID: {task.id}, Title: {task.title}, Completed: {task.completed}, User ID: {task.user_id}")

        return True

    except SQLAlchemyError as e:
        print(f"ERROR: Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False

def check_environment():
    """Check environment variables and settings"""
    print("\nChecking environment settings...")
    print(f"Database URL configured: {'Yes' if settings.DATABASE_URL else 'No'}")
    print(f"Secret Key configured: {'Yes' if settings.SECRET_KEY and len(settings.SECRET_KEY) > 10 else 'No'}")
    print(f"Algorithm: {settings.ALGORITHM}")
    print(f"Token Expiry Minutes: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")

if __name__ == "__main__":
    print("=== Database Connection Test ===")
    check_environment()
    success = test_database_connection()

    if success:
        print("\nSUCCESS: Database verification completed successfully!")
    else:
        print("\nERROR: Database verification failed!")