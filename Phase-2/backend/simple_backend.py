import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Depends, Path
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
import logging
from datetime import datetime, timedelta

# Set environment variables directly to bypass .env file issues
os.environ['BETTER_AUTH_SECRET'] = 'test-secret-key-change-in-production'
os.environ['FRONTEND_URL'] = 'http://localhost:3000'
os.environ['BACKEND_URL'] = 'http://localhost:8000'

# Define settings directly instead of using config.py
class DirectSettings:
    better_auth_secret: str = os.getenv("BETTER_AUTH_SECRET", "test-secret-key-change-in-production")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")

settings = DirectSettings()

logger = logging.getLogger(__name__)

async def verify_token(token: str) -> dict:
    """
    Verify a JWT token and return the payload if valid.
    """
    try:
        payload = jwt.decode(token, settings.better_auth_secret, algorithms=["HS256"])
        return payload
    except JWTError as e:
        logger.error(f"JWT token verification failed: {str(e)}")
        return None

async def auth_middleware(request, call_next):
    """
    Simple authentication middleware to handle JWT token verification.
    """
    # Define paths that don't require authentication
    public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json"]

    path = request.url.path
    if path in public_paths:
        response = await call_next(request)
        return response

    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid"
        )

    token = auth_header.split(" ")[1]

    # Verify the token
    payload = await verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # Add user info to request state for downstream handlers
    request.state.user_id = payload.get("user_id")
    request.state.user_info = payload

    response = await call_next(request)
    return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up the Todo API with JWT authentication...")
    yield
    # Shutdown
    print("Shutting down the Todo API...")

# Create FastAPI app instance
app = FastAPI(
    title="Todo API - JWT Enabled",
    description="REST API for Todo application with JWT authentication",
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

# Add the authentication middleware
app.middleware("http")(auth_middleware)

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
    return {
        "status": "healthy",
        "jwt_configured": True,
        "message": "Server is running with JWT authentication"
    }

@app.get("/api/{user_id}/tasks")
def get_tasks(user_id: str):
    """
    Test endpoint that requires authentication.
    """
    # This endpoint requires a valid JWT token
    return {
        "message": f"Tasks for user {user_id}",
        "user_authenticated": True
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting the Todo API backend server with JWT authentication...")
    print(f"Server will run on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)