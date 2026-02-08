import os
from sqlmodel import select
from db import engine, create_db_and_tables
from models import User, Task
from sqlmodel import Session

# Set the database URL to use Neon
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_1wiNqRWc4MPh@ep-sparkling-term-a4onppqn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'

print("Creating tables...")
create_db_and_tables()

print("Testing database connection...")

# Test creating a session and querying
with Session(engine) as session:
    # Test if we can query users
    try:
        users = session.exec(select(User)).all()
        print(f"Found {len(users)} users in database")

        # Test if we can query tasks
        tasks = session.exec(select(Task)).all()
        print(f"Found {len(tasks)} tasks in database")

        print("Database connection test successful!")
    except Exception as e:
        print(f"Database query failed: {e}")
        import traceback
        traceback.print_exc()