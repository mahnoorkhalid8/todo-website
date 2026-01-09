from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

# Handle imports for both local development and Hugging Face deployment
# This approach handles different ways the module can be imported
try:
    # Try relative imports first (works when running as a package)
    from .db import create_db_and_tables
    from .routes import auth, tasks
    from .config import settings
except ImportError:
    # Fall back to absolute imports (works when running directly)
    import sys
    import os
    # Add the backend directory to the path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from db import create_db_and_tables
    from routes import auth, tasks
    from config import settings


def create_app():
    app = FastAPI(
        title="Todo Web Application API",
        description="API for the Todo Web Application with user authentication and task management",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": {"code": "NOT_FOUND", "message": "Resource not found"}}
        )


    @app.on_event("startup")
    def on_startup():
        create_db_and_tables()

    @app.get("/")
    def read_root():
        return {"message": "Todo Web Application API", "version": "1.0.0"}

    @app.get("/health")
    def health_check():
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True
    )