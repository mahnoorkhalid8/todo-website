#!/bin/bash
# Script to run the Todo App with SQLite for local development

echo "Starting Todo App - Full Stack with SQLite"
echo "=========================================="

# Create a temporary .env file for local development
cat > backend/.env.local << EOF
DATABASE_URL=sqlite:///./todo_app_local.db
SECRET_KEY=your-local-super-secret-jwt-key-for-development
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

echo "Created local environment file..."

# Start backend with SQLite
echo "Starting backend server with SQLite..."
cd backend
echo "Running: DATABASE_URL=sqlite:///./todo_app_local.db python -m uvicorn main:app --reload --port 8000"
DATABASE_URL=sqlite:///./todo_app_local.db python -m uvicorn main:app --reload --port 8000 &

BACKEND_PID=$!

# Give backend time to start
sleep 3

# Start frontend in another terminal
echo "Starting frontend server..."
cd ../frontend
npm run dev

# Cleanup when done
kill $BACKEND_PID 2>/dev/null
rm -f ../backend/.env.local

echo "Applications stopped."