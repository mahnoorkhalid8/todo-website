import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Get the database URL
DATABASE_URL = os.getenv('DATABASE_URL')
print(f"Database URL: {DATABASE_URL}")

if 'neon.tech' in DATABASE_URL:
    print("SUCCESS: Database URL appears to be a Neon database")
else:
    print("ERROR: Database URL does not appear to be a Neon database")

# Test synchronous connection
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()
        print(f"SUCCESS: Successfully connected to database!")
        print(f"Database version: {version[0][:100]}...")

        # Test if tables exist by querying information schema
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables in database: {tables}")

except Exception as e:
    print(f"ERROR: Database connection failed: {e}")

# Test with async engine (used by FastAPI/SQLModel)
try:
    async_engine = create_async_engine(DATABASE_URL)

    async def test_connection():
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.fetchone()
            print(f"SUCCESS: Async connection successful!")
            print(f"Async database version: {version[0][:100]}...")

            # Test if tables exist
            result = await conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"Tables in async connection: {tables}")

    asyncio.run(test_connection())

except Exception as e:
    print(f"ERROR: Async database connection failed: {e}")