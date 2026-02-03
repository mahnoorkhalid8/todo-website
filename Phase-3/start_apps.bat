@echo off
echo Starting Todo App - Backend and Frontend
echo ========================================

REM Start backend on port 8000 (or alternative if in use)
echo Starting backend server...
cd backend
start cmd /k "python -m uvicorn main:app --reload --port 8000 --host 127.0.0.1"

timeout /t 5 /nobreak >nul

REM Start frontend on port 3000 (or alternative if in use)
echo Starting frontend server...
cd ../frontend
start cmd /k "set PORT=3000 && npm run dev"

echo.
echo Applications should be starting...
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:3000 (or next available port if 3000 is in use)
echo.
echo Press Ctrl+C to stop the applications.
pause