import os
import sys

# Set environment variables before any other imports
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_1wiNqRWc4MPh@ep-sparkling-term-a4onppqn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'
os.environ['SECRET_KEY'] = 'o2nmkwIUqotG5dDCWR0a0rk2Uk2rL0DPBvqbdkwZ54N'

def run_server():
    # Force reimport of db module to pick up the new environment variables
    import importlib

    # Import and run the app
    import uvicorn
    from main import app

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    run_server()