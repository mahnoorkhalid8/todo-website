#!/usr/bin/env python3
"""
Direct test to simulate the API task creation process
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_task_creation_direct():
    """Test task creation the same way the API does it"""
    try:
        print("=== Direct Task Creation Test ===")

        # Import the same modules as the API
        from dependencies.auth import get_current_user
        from dependencies.database import get_db_session
        from services.task_service import create_task
        from models import User
        from sqlmodel import Session

        # Simulate the same process as the API endpoint
        from db import get_session
        from services.auth_service import create_user

        # Create a test user first
        with get_session() as session:
            test_user = create_user(
                session=session,
                email=f"apitest_{str(int(time.time()))}@example.com",
                password="TestPassword123!",
                name="API Test User"
            )
            print(f"Created test user: {test_user.email}")

            # Now try to create a task the same way the API endpoint does
            try:
                from datetime import datetime
                task = create_task(
                    session=session,  # Same session
                    user_id=test_user.id,
                    title="API Test Task",
                    description="Test task created the same way as API",
                    due_date=None
                )
                print(f"Task created successfully: {task.title}")
                print(f"Task ID: {task.id}")

                # Clean up
                session.delete(task)
                session.delete(test_user)
                session.commit()
                print("Cleaned up test data successfully")

                return True

            except Exception as e:
                print(f"Error creating task: {e}")
                import traceback
                traceback.print_exc()
                return False

    except Exception as e:
        print(f"Error in direct test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_task_creation_direct()
    if success:
        print("\n[SUCCESS] Direct task creation test passed!")
    else:
        print("\n[ERROR] Direct task creation test failed!")
        sys.exit(1)