import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create a minimal FastAPI app for health check
app = FastAPI(
    title="Todo API - Health Check",
    description="Minimal API for health check without database dependencies",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """
    Root endpoint for health check.
    """
    return {"message": "Todo API is running (minimal version)"}

@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "message": "Server is running"
    }

if __name__ == "__main__":
    print("Starting minimal Todo API backend server for health check...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)