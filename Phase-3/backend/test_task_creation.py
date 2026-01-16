import os
from sqlmodel import Session
from db import engine, create_db_and_tables
from services.task_service import create_task

# Set the database URL to use Neon
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_1wiNqRWc4MPh@ep-sparkling-term-a4onppqn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'

print("Testing task creation directly...")

# Create a test user ID
test_user_id = "377bb932-ffc8-4c1a-8784-4319d67972dd"  # The user we created earlier

try:
    with Session(engine) as session:
        print("Creating task via service...")
        task = create_task(session, test_user_id, "Direct Test Task", "Test description")
        print(f"Task created successfully: {task.title} (ID: {task.id})")
except Exception as e:
    print(f"Task creation failed: {e}")
    import traceback
    traceback.print_exc()