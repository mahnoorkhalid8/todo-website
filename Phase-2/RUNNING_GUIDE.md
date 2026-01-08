# Running the Todo App - Full Stack Guide

## Prerequisites
- Node.js (v16 or higher) for the frontend
- Python 3.11 for the backend
- npm or yarn package manager

## Setup Instructions

### 1. Backend Setup (Python FastAPI)
```bash
# Navigate to backend directory
cd backend/

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python -m uvicorn main:app --reload --port 8000
```

The backend will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 2. Frontend Setup (Next.js)
```bash
# Open a new terminal/command prompt
# Navigate to frontend directory
cd frontend/

# Install JavaScript dependencies
npm install

# Start the frontend development server
npm run dev
```

The frontend will be available at:
- UI: http://localhost:3000

### 3. Alternative: Using Docker Compose (Recommended)
```bash
# From the root directory, run:
docker-compose up --build
```

This will start all services (backend, frontend, and database) simultaneously.

## Environment Variables

For the backend, you may need to set these environment variables:
- `DATABASE_URL`: PostgreSQL database connection string
- `SECRET_KEY`: JWT signing key (at least 32 characters)
- `ALLOWED_ORIGINS`: List of allowed origins for CORS

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register new user
- POST `/api/auth/login` - Login user
- POST `/api/auth/logout` - Logout user

### Tasks
- GET `/api/tasks/` - Get all tasks for current user
- POST `/api/tasks/` - Create new task
- GET `/api/tasks/{task_id}` - Get specific task
- PUT `/api/tasks/{task_id}` - Update task
- DELETE `/api/tasks/{task_id}` - Delete task
- PATCH `/api/tasks/{task_id}/complete` - Toggle task completion

## Troubleshooting

1. **Port Already in Use**: If you get port binding errors, try different ports:
   - Backend: Change `--port 8000` to another port
   - Frontend: Will typically auto-increment to 3001, 3002, etc.

2. **Database Connection Issues**: Make sure PostgreSQL is running and accessible.

3. **Dependency Issues**: Make sure to install all dependencies in both frontend and backend directories.

4. **Cross-Origin Issues**: Check that the frontend URL is in the ALLOWED_ORIGINS in the backend config.