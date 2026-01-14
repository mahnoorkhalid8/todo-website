from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
import os

# Define the security scheme globally
security_scheme = HTTPBearer()

def create_app():
    app = FastAPI(
        title="Todo Web Application API",
        description="API for the Todo Web Application with user authentication and task management",
        version="1.0.0"
    )

    # Add CORS middleware
    # Handle imports for both local development and Hugging Face deployment
    try:
        # Try relative imports first (works when running as a package)
        from .config import settings
    except ImportError:
        # Fall back to absolute imports (works when running directly)
        import sys
        import os
        # Add the backend directory to the path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from config import settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://todo-website-blush.vercel.app",
            "https://mahnoorkhalid8-todo-website.hf.space",
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import and include routers after middleware setup
    # This helps avoid circular imports and early model loading
    try:
        # Try relative imports first (works when running as a package)
        from .db import create_db_and_tables
        from .routes import auth, tasks
        # Import models to register them with SQLModel before creating tables
        from . import models
    except ImportError:
        # Fall back to absolute imports (works when running directly)
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from db import create_db_and_tables
        from routes import auth, tasks
        # Import models to register them with SQLModel before creating tables
        import models

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

    # Custom OpenAPI schema from the predefined schema file
    import json
    import os

    def custom_openapi():
        # Try to load the predefined schema from api_documentation.json if it exists
        schema_file_path = os.path.join(os.path.dirname(__file__), "..", "api_documentation.json")
        if os.path.exists(schema_file_path):
            try:
                with open(schema_file_path, 'r') as f:
                    predefined_schema = json.load(f)
                app.openapi_schema = predefined_schema
                return app.openapi_schema
            except Exception as e:
                print(f"Could not load predefined schema, falling back to auto-generation: {e}")

        # Fallback to auto-generation
        openapi_schema = get_openapi(
            title="Todo Web Application API",
            version="1.0.0",
            description="API for the Todo Web Application with user authentication and task management",
            routes=app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "HTTPBearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
        # Apply security globally or to specific routes that need authentication
        for path in openapi_schema["paths"]:
            for method in openapi_schema["paths"][path]:
                if path.startswith("/api/tasks"):  # Protect task endpoints
                    openapi_schema["paths"][path][method]["security"] = [{"HTTPBearer": []}]
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

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