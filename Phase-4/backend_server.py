import os
import sys
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add the backend directory to path to resolve imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.db import create_db_and_tables
from backend.routes import auth, tasks
try:
    from backend.routes import chat
except ImportError:
    # Chat route might not exist yet
    chat = None
from backend.config import settings

def create_app_without_startup_event():
    app = FastAPI(
        title="Todo Web Application API",
        description="API for the Todo Web Application with user authentication and task management",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://todo-website-blush.vercel.app",
            "https://mahnoorkhalid8-todo-website.hf.space"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])

    # Include chat router if available
    if chat:
        app.include_router(chat.router, prefix="/api/chat", tags=["Chatbot"])

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": {"code": "NOT_FOUND", "message": "Resource not found"}}
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}}
        )

    # Don't add the startup event that creates DB tables to avoid connection issues
    # @app.on_event("startup")
    # def on_startup():
    #     create_db_and_tables()

    @app.get("/")
    def read_root():
        return {"message": "Todo Web Application API", "version": "1.0.0"}

    @app.get("/health")
    def health_check():
        return {"status": "healthy"}

    return app

app = create_app_without_startup_event()

if __name__ == "__main__":
    uvicorn.run(
        "backend_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )