@echo off
REM Script to start both frontend and backend servers

echo Starting Todo App with AI Assistant...

REM Start backend server in a new window
start cmd /k "cd backend && python -m uvicorn main:app --reload --port 8000"

REM Give backend a moment to start
timeout /t 3 /nobreak >nul

REM Start frontend server in a new window
start cmd /k "cd frontend && npm run dev"

echo.
echo Applications are starting...
echo Backend will be available at: http://127.0.0.1:8000
echo Frontend will be available at: http://localhost:3000
echo.
echo The AI Assistant is integrated and ready to help manage your tasks!