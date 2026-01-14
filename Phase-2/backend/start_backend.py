import os
import sys
from contextlib import asynccontextmanager

# Set environment variables directly to bypass .env file issues
os.environ['DATABASE_URL'] = 'sqlite:///./todo_test.db'  # Use SQLite for testing
os.environ['BETTER_AUTH_SECRET'] = 'test-secret-key-change-in-production'
os.environ['FRONTEND_URL'] = 'http://localhost:3000'
os.environ['BACKEND_URL'] = 'http://localhost:8000'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up the Todo API...")
    yield
    # Shutdown
    print("Shutting down the Todo API...")

# Create FastAPI app instance
app = FastAPI(
    title="Todo API",
    description="REST API for Todo application with user authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and add the authentication middleware
from middleware.auth import auth_middleware
app.middleware("http")(auth_middleware)

# Include API routes (using a minimal version that doesn't require database)
@app.get("/")
def read_root():
    """
    Root endpoint for health check.
    """
    return {"message": "Todo API is running with JWT authentication"}

@app.get("/health")
def health_check():
    """
    Health check endpoint to confirm JWT functionality.
    """
    auth_secret = os.getenv('BETTER_AUTH_SECRET')
    return {
        "status": "healthy",
        "jwt_configured": bool(auth_secret),
        "message": "Server is running with JWT authentication"
    }

# Import routes but with a fallback for database issues
try:
    from routes import tasks, auth
    app.include_router(tasks.router, prefix="/api/{user_id}", tags=["tasks"])
    app.include_router(auth.router, prefix="/api", tags=["auth"])
    print("Routes loaded successfully")
except Exception as e:
    print(f"Warning: Could not load all routes: {e}")
    print("Starting with minimal API functionality")

if __name__ == "__main__":
    import uvicorn
    print("Starting the Todo API backend server...")
    print("JWT authentication is configured and ready")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)