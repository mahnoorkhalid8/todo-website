import os
import sys

# Set environment variables
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_1wiNqRWc4MPh@ep-sparkling-term-a4onppqn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'
os.environ['SECRET_KEY'] = 'o2nmkwIUqotG5dDCWR0a0rk2Uk2rL0DPBvqbdkwZ54N'

def test_db_connection():
    try:
        # Import the database module
        from db import engine, create_db_and_tables
        print("Successfully imported database modules")

        # Test the connection
        with engine.connect() as conn:
            print("Successfully connected to database")
            result = conn.execute("SELECT 1")
            print("Database query successful:", result.fetchone())

        # Try to create tables
        print("Attempting to create tables...")
        create_db_and_tables()
        print("Table creation attempt completed")

        # Check if tables exist
        from sqlmodel import SQLModel
        from models import User, Task  # Import the models

        print("Models imported successfully")
        print("User table name:", User.__tablename__ if hasattr(User, '__tablename__') else 'No table name')
        print("Task table name:", Task.__tablename__ if hasattr(Task, '__tablename__') else 'No table name')

        # List tables in the metadata
        print("Tables in metadata:", list(SQLModel.metadata.tables.keys()))

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_db_connection()