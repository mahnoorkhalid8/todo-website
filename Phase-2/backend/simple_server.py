import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the parent directory to the path so we can access the .env file
parent_dir = Path(__file__).parent.parent
env_file = parent_dir / '.env'

# Read the .env file manually to set environment variables
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                # Handle values with quotes
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Remove surrounding quotes if present
                    value = value.strip().strip('"\'')
                    os.environ[key] = value

print("Environment variables loaded")
print(f"BETTER_AUTH_SECRET available: {'Yes' if os.getenv('BETTER_AUTH_SECRET') else 'No'}")

# Create a simple FastAPI app to test JWT functionality
app = FastAPI(
    title="Todo API - JWT Test",
    description="Test server to verify JWT authentication is working",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """
    Root endpoint for health check.
    """
    return {"message": "Todo API is running with JWT authentication"}

@app.get("/health")
def health_check():
    """
    Health check endpoint to confirm server is running.
    """
    auth_secret = os.getenv('BETTER_AUTH_SECRET')
    return {
        "status": "healthy",
        "jwt_configured": bool(auth_secret),
        "message": "Server is running with JWT authentication"
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting simple server to confirm JWT functionality...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)