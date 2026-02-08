import uvicorn
import os
import sys
from backend.main import app

# Remove the startup event that creates tables to avoid connection issues on startup
@app.on_event("startup")
def skip_db_init():
    print("Skipping initial database connection to avoid startup issues...")
    pass  # Skip the database initialization that was causing startup problems

if __name__ == "__main__":
    # Set the environment to load the .env file
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )