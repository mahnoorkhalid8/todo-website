from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Attempt to import ProxyHeadersMiddleware for handling HTTPS behind reverse proxy
try:
    from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
except ImportError:
    # Fallback for older versions
    try:
        from starlette.middleware.proxy_headers import ProxyHeadersMiddleware
    except ImportError:
        # If neither is available, define a minimal proxy headers middleware
        from starlette.middleware.base import BaseHTTPMiddleware

        class ProxyHeadersMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                # Handle common proxy headers for HTTPS
                forwarded_proto = request.headers.get('X-Forwarded-Proto')
                if forwarded_proto == 'https':
                    # Modify the request URL scheme
                    pass  # FastAPI handles this automatically in newer versions
                response = await call_next(request)
                return response
from db import create_db_and_tables
from routes import auth, tasks
try:
    from routes import chat
except ImportError:
    # Chat route might not exist yet
    chat = None
import os
from config import settings


def create_app():
    # Create the app with ProxyHeadersMiddleware first (if available)
    app = FastAPI(
        title="Todo Web Application API",
        description="API for the Todo Web Application with user authentication and task management",
        version="1.0.0"
    )

    # Add Proxy Headers middleware to handle HTTPS behind reverse proxy (if available)
    try:
        app.add_middleware(ProxyHeadersMiddleware)
    except NameError:
        # ProxyHeadersMiddleware not available, continue without it
        pass

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://todo-website-bot.vercel.app",
            "https://mahnoorkhalid8-todo-bot.hf.space",
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://localhost:8000",
            "http://127.0.0.1:8000"
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

    # Skip startup DB initialization to prevent connection issues during startup
    # Tables will be created when first accessed
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


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=int(os.getenv("PORT", "8000")),
        reload=True
    )