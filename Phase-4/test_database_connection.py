import os
import sys
sys.path.append("C:/Users/SEVEN86 COMPUTES/todo-app/Phase-3/backend")
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, select
from models import Task, User, Conversation, Message

# Load environment variables
load_dotenv("C:/Users/SEVEN86 COMPUTES/todo-app/Phase-3/backend/.env")

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_1wiNqRWc4MPh@ep-sparkling-term-a4onppqn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require")

print(f"Attempting to connect to database: {DATABASE_URL}")

try:
    # Create engine
    engine = create_engine(DATABASE_URL)

    # Test the connection
    with Session(engine) as session:
        print("✅ Successfully connected to the database!")

        # Try to count users
        try:
            user_count = session.exec(select(User)).all()
            print(f"📊 Number of users in database: {len(user_count)}")
        except Exception as e:
            print(f"⚠️  Could not query users table: {e}")

        # Try to count tasks
        try:
            task_count = session.exec(select(Task)).all()
            print(f"📊 Number of tasks in database: {len(task_count)}")

            if len(task_count) > 0:
                print("📋 Sample of existing tasks:")
                for i, task in enumerate(task_count[:5]):  # Show first 5 tasks
                    print(f"  - ID: {task.id}, Title: {task.title}, Completed: {task.completed}, User: {task.user_id}")
            else:
                print("📋 No tasks found in the database")

        except Exception as e:
            print(f"⚠️  Could not query tasks table: {e}")

        # Try to count conversations
        try:
            conversation_count = session.exec(select(Conversation)).all()
            print(f"📊 Number of conversations in database: {len(conversation_count)}")
        except Exception as e:
            print(f"⚠️  Could not query conversations table: {e}")

        # Try to count messages
        try:
            message_count = session.exec(select(Message)).all()
            print(f"📊 Number of messages in database: {len(message_count)}")
        except Exception as e:
            print(f"⚠️  Could not query messages table: {e}")

except Exception as e:
    print(f"❌ Failed to connect to database: {e}")
    print("\nPossible reasons:")
    print("- Invalid credentials in the connection string")
    print("- Network/firewall issues preventing connection")
    print("- Neon database might not be properly configured")
    print("- The database might be temporarily unavailable")