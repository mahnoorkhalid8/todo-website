from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import socket
from contextlib import closing
from dotenv import load_dotenv

def check_port(port):
    """Check if a port is available"""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        result = sock.connect_ex(('127.0.0.1', port))
        return result != 0

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}

if __name__ == "__main__":
    import uvicorn

    # Try to use port 8000, but if it's not available, try alternatives
    ports_to_try = [8000, 8001, 8002]
    selected_port = None

    for port in ports_to_try:
        if check_port(port):
            selected_port = port
            break

    if selected_port is None:
        # If no ports are available, try to use 8000 and allow uvicorn to handle conflicts
        selected_port = 8000

    print(f"Attempting to start server on port {selected_port}")
    print("Environment variables loaded")
    print(f"BETTER_AUTH_SECRET available: {'Yes' if os.getenv('BETTER_AUTH_SECRET') else 'No'}")
    print("Starting simple server to confirm JWT functionality...")

    uvicorn.run(app, host="0.0.0.0", port=selected_port)