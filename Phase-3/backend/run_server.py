import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set the database URL to use SQLite
os.environ.setdefault('DATABASE_URL', 'sqlite:///./todo_app_local.db')

# Set host and port
host = os.getenv('HOST', '127.0.0.1')
port = int(os.getenv('PORT', '8000'))

# Import and run the app
try:
    from main import app
    import uvicorn

    print(f"Starting server on {host}:{port}")
    print(f"Using database: {os.getenv('DATABASE_URL')}")

    uvicorn.run(app, host=host, port=port, reload=True)
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)