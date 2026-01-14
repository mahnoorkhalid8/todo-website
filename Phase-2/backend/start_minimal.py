import os
import sys
import uvicorn

# Temporarily remove .env from the current directory to avoid conflicts
env_file_path = os.path.join(os.getcwd(), '.env')
env_backup_path = os.path.join(os.getcwd(), '.env.backup')

# Check if .env exists in current directory and move it
if os.path.exists(env_file_path):
    os.rename(env_file_path, env_backup_path)
    print("Backed up .env file to .env.backup")

try:
    # Set minimal required environment variables
    os.environ['DATABASE_URL'] = 'sqlite:///./todo_test.db'
    os.environ['BETTER_AUTH_SECRET'] = 'test-secret-key-change-in-production'
    os.environ['JWT_SECRET'] = 'test-jwt-secret-key-change-in-production'
    os.environ['FRONTEND_URL'] = 'http://localhost:3000'
    os.environ['BACKEND_URL'] = 'http://localhost:8000'
    os.environ['NODE_ENV'] = 'development'

    # Import and run the main app
    from main import app

    print("Starting the Todo API backend server with test configuration...")
    print("Database URL:", os.environ.get('DATABASE_URL'))
    print("Frontend URL:", os.environ.get('FRONTEND_URL'))
    print("Backend URL:", os.environ.get('BACKEND_URL'))

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

finally:
    # Restore the .env file if it was backed up
    if os.path.exists(env_backup_path):
        os.rename(env_backup_path, env_file_path)
        print("Restored .env file from .env.backup")