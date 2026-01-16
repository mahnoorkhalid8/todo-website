@echo off
echo Starting Todo App - Full Stack
echo ==============================

echo Setting up environment variables...
set DATABASE_URL=postgresql://user:password@localhost:5432/todo_app
set SECRET_KEY=your-super-secret-jwt-signing-key-that-is-at-least-32-characters-long

echo.
echo Starting Backend Server...
echo =========================
cd backend
start "Backend Server" cmd /k "python -m uvicorn main:app --reload --port 8000"

timeout /t 5 /nobreak >nul

echo.
echo Starting Frontend Server...
echo =========================
cd ../frontend
start "Frontend Server" cmd /k "npm run dev"

echo.
echo Applications are starting...
echo - Backend API: http://localhost:8000
echo - Frontend UI: http://localhost:3000
echo - API Documentation: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul