import subprocess
import time
import os
import signal
import sys

def start_backend():
    """Start the backend server"""
    print("Starting backend server on port 8001...")
    backend_env = os.environ.copy()
    backend_env["PORT"] = "8001"

    backend_process = subprocess.Popen([
        "python", "-m", "uvicorn", "main:app",
        "--reload", "--port", "8001", "--host", "127.0.0.1"
    ], cwd="./backend", env=backend_env)

    return backend_process

def start_frontend():
    """Start the frontend server"""
    print("Starting frontend server on port 3001...")
    frontend_env = os.environ.copy()
    frontend_env["PORT"] = "3001"

    frontend_process = subprocess.Popen([
        "npm", "run", "dev"
    ], cwd="./frontend", env=frontend_env)

    return frontend_process

if __name__ == "__main__":
    print("Starting Todo App - Backend and Frontend")
    print("========================================")

    # Start backend
    backend_proc = start_backend()
    time.sleep(3)  # Give backend time to start

    # Start frontend
    frontend_proc = start_frontend()

    print("\nApplications started!")
    print(f"Backend: http://127.0.0.1:8001")
    print(f"Frontend: http://localhost:3001")
    print("\nPress Ctrl+C to stop the applications.")

    try:
        # Wait for both processes
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nTerminating applications...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Applications terminated.")