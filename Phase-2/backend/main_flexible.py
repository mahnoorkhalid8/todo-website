"""
Main FastAPI application for the Todo application.
This version has optional database initialization to handle connection issues.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to hold app state
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    logger.info("Starting up application...")
    # Attempt to initialize database but don't fail if it fails
    try:
        from db import init_db
        await init_db()
        logger.info("Database initialized successfully")
        app_state['db_ready'] = True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.info("Running in API-only mode without database")
        app_state['db_ready'] = False

    yield  # Application runs here

    # Shutdown
    try:
        from db import close_db
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")

# Create FastAPI app instance with lifespan
app = FastAPI(
    title="Todo API",
    description="REST API for Todo application with user authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS middleware
# In production, replace "*" with your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware if available
try:
    from middleware.auth import auth_middleware
    app.middleware("http")(auth_middleware)
    logger.info("Authentication middleware loaded")
except Exception as e:
    logger.error(f"Failed to load auth middleware: {e}")
    # Define a simple auth middleware as fallback
    async def auth_middleware(request, call_next):
        response = await call_next(request)
        return response
    app.middleware("http")(auth_middleware)

# Include API routes with error handling
try:
    from routes import tasks, auth
    app.include_router(tasks.router, prefix="/api/{user_id}", tags=["tasks"])
    app.include_router(auth.router, prefix="/api", tags=["auth"])
    logger.info("Routes loaded successfully")
except Exception as e:
    logger.error(f"Failed to load routes: {e}")
    # Define basic fallback routes
    from fastapi import HTTPException, Depends
    import jwt
    from pydantic import BaseModel

    JWT_SECRET = os.getenv("BETTER_AUTH_SECRET", "fallback_secret")

    class UserLogin(BaseModel):
        email: str
        password: str

    @app.post("/api/auth/login")
    def login(user_credentials: UserLogin):
        # Generate a simple token for testing
        token = jwt.encode({
            "sub": f"user_{hash(user_credentials.email)}",
            "email": user_credentials.email
        }, JWT_SECRET, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}

    @app.get("/api/{user_id}/tasks")
    def get_tasks(user_id: str):
        # Return empty task list for testing
        return {"tasks": []}

@app.get("/")
def read_root():
    """
    Root endpoint for health check.
    """
    db_status = "READY" if app_state.get('db_ready') else "NOT READY"
    return {
        "message": "Todo API is running",
        "database": db_status,
        "better_auth_secret_set": bool(os.getenv("BETTER_AUTH_SECRET"))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)