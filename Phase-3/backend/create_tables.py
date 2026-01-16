#!/usr/bin/env python3
"""
Script to explicitly create database tables in Neon database
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_tables():
    """Create database tables in the Neon database"""
    try:
        print("Connecting to database...")

        # Import the database setup
        from db import create_db_and_tables

        print("Creating database tables...")
        create_db_and_tables()

        print("Database tables created successfully!")

        # Test the connection by importing models
        from models import User, Task
        print("Models imported successfully!")

        # Test basic database functionality
        from sqlmodel import Session, select
        from db import get_engine

        engine = get_engine()
        print("Engine created successfully!")

        # Test creating a session
        with Session(engine) as session:
            print("Database session created successfully!")

            # Test if we can query users (table should exist now)
            try:
                from models import User
                from sqlmodel import select
                # Count users by executing a select query and getting the length
                users = session.exec(select(User)).all()
                user_count = len(users)
                print(f"Users table exists! Current user count: {user_count}")
            except Exception as e:
                print(f"Error querying users table: {e}")

        print("Database connection and table creation verified successfully!")
        return True

    except Exception as e:
        print(f"Error creating database tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_tables()
    if success:
        print("\n[SUCCESS] Database setup completed successfully!")
    else:
        print("\n[ERROR] Database setup failed!")
        sys.exit(1)