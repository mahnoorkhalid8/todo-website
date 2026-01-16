#!/usr/bin/env python3
"""Start the backend server with Neon database configuration."""

import os
import sys

# Set environment variables before any imports
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_1wiNqRWc4MPh@ep-sparkling-term-a4onppqn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'
os.environ['SECRET_KEY'] = 'o2nmkwIUqotG5dDCWR0a0rk2Uk2rL0DPBvqbdkwZ54N'

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    import uvicorn

    # Import main after environment variables are set
    from main import app

    print("Starting server with Neon database configuration...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()