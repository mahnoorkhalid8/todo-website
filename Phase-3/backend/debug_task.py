#!/usr/bin/env python3
"""
Debug script to test task creation directly
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_task_creation():
    """Debug task creation process"""
    try:
        print("=== Debugging Task Creation ===")

        # Import necessary modules
        from config import settings
        print(f"DATABASE_URL from settings: {settings.DATABASE_URL}")

        # Import models and services
        from models import Task, User
        from services.task_service import create_task
        from db import get_session
        from datetime import datetime

        # Create a test user first using auth service
        from services.auth_service import create_user

        with get_session() as session:
            # Create a test user
            test_user = create_user(
                session=session,
                email=f"test_task_{str(datetime.now().timestamp())}@example.com",
                password="TestPassword123!",
                name="Test Task User"
            )
            print(f"Created test user: {test_user.email}")

            # Now try to create a task for this user
            try:
                from datetime import datetime
                task = create_task(
                    session=session,
                    user_id=test_user.id,
                    title="Debug Task",
                    description="Debug task for testing",
                    due_date=None  # Not providing due_date to avoid any datetime issues
                )
                print(f"Task created successfully: {task.title}")
                print(f"Task ID: {task.id}")
                print(f"Task user_id: {task.user_id}")

                # Clean up: delete the test task and user
                session.delete(task)
                session.delete(test_user)
                session.commit()
                print("Cleaned up test data successfully")

            except Exception as e:
                print(f"Error creating task: {e}")
                import traceback
                traceback.print_exc()
                return False

        print("\n[SUCCESS] Task creation debugging completed!")
        return True

    except Exception as e:
        print(f"[ERROR] Error in task debugging: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_task_creation()
    if success:
        print("\n[SUCCESS] Task creation debugging completed successfully!")
    else:
        print("\n[ERROR] Task creation debugging failed!")
        sys.exit(1)