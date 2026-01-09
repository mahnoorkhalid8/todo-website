import os
import sys

# Set environment variables before importing any other modules
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_1wiNqRWc4MPh@ep-sparkling-term-a4onppqn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'
os.environ['SECRET_KEY'] = 'o2nmkwIUqotG5dDCWR0a0rk2Uk2rL0DPBvqbdkwZ54N'

# Now import and run the application
if __name__ == "__main__":
    import uvicorn

    # Import after setting environment variables
    from main import app

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)