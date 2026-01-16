#!/usr/bin/env python3
"""
Development startup script for the backend
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables for development
os.environ.setdefault('DATABASE_URL', 'sqlite:///./todo_app_local.db')
os.environ.setdefault('SECRET_KEY', 'dev-secret-key-change-in-production')
os.environ.setdefault('ALGORITHM', 'HS256')
os.environ.setdefault('ACCESS_TOKEN_EXPIRE_MINUTES', '30')

def start_server():
    """Start the development server"""
    try:
        import uvicorn

        # Start the server with reload enabled
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["."],
            log_level="info"
        )
    except ImportError as e:
        print(f"Error importing uvicorn: {e}")
        print("Please make sure you have installed the required dependencies:")
        print("pip install fastapi uvicorn sqlmodel python-jose[cryptography] passlib[bcrypt] python-multipart python-dotenv")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("Starting development server on http://0.0.0.0:8000")
    start_server()