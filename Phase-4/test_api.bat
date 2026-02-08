@echo off
REM Test script to verify the Todo App API is working correctly
echo Testing Todo App API...

echo.
echo 1. Checking API health...
curl -s -X GET "http://127.0.0.1:8000/health" | python -m json.tool

echo.
echo 2. Testing unauthenticated access (should return 403)...
curl -s -o nul -w "Status Code: %{http_code}\n" -X POST "http://127.0.0.1:8000/api/tasks/" -H "Content-Type: application/json" -d "{\"title\":\"Test\"}"

echo.
echo 3. Instructions for manual task creation:
echo    - Register: curl -X POST 'http://127.0.0.1:8000/api/auth/register' -H 'Content-Type: application/json' -d '{\"email\":\"test@example.com\",\"password\":\"Password123!\",\"name\":\"Test User\"}'
echo    - Login: curl -X POST 'http://127.0.0.1:8000/api/auth/login' -H 'Content-Type: application/json' -d '{\"email\":\"test@example.com\",\"password\":\"Password123!\"}'
echo    - Create Task: curl -X POST 'http://127.0.0.1:8000/api/tasks/' -H 'Content-Type: application/json' -H 'Authorization: Bearer YOUR_TOKEN' -d '{\"title\":\"Test Task\"}'

echo.
echo Test complete. If you're still getting errors:
echo - Check that both servers are running (backend on port 8000, frontend on port 3000)
echo - Verify you have a valid authentication token
echo - Ensure your request has the correct format with required 'title' field
echo - Remember tokens expire - you may need to log in again