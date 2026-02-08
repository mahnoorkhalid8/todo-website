import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

# Temporarily disable the startup event that creates database tables
# by patching the function before importing
import backend.main
from backend.db import create_db_and_tables

# Store the original function
original_on_startup = getattr(backend.main, 'on_startup', None)

# Replace with a no-op function
def no_op_startup():
    print("Database initialization deferred to avoid startup connection issues")
    print("Neon database connection will be handled on-demand")

# Replace the startup function
backend.main.on_startup = no_op_startup

# Now import and run the app
from backend.main import app
import uvicorn

if __name__ == "__main__":
    print("Starting backend server with Neon database (connection deferred)...")
    print("Server will be available at http://127.0.0.1:8000")
    print("Database connection will be established when first accessed")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)