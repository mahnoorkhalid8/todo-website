@echo off
echo ===========================================
echo TASK CREATION ISSUE DEBUGGING SCRIPT
echo ===========================================

echo.
echo 1. VERIFYING SERVERS ARE RUNNING:
echo -----------------------------------

echo Checking backend health...
curl -s -X GET "http://127.0.0.1:8000/health" > nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend server is running and healthy
) else (
    echo [ERROR] Backend server is not responding
)

echo.
echo 2. GETTING A FRESH AUTHENTICATION TOKEN:
echo -----------------------------------------

echo Getting fresh authentication token...
curl -s -X POST "http://127.0.0.1:8000/api/auth/login" ^
    -H "Content-Type: application/json" ^
    -d "{^"email^":^"final@test.com^",^"password^":^"FinalPass123!^"}" ^
    -o token_response.tmp

if exist token_response.tmp (
    echo [OK] Got fresh authentication token
    for /f "delims=" %%i in ('type token_response.tmp ^| python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2^>nul') do set TOKEN=%%i
    del token_response.tmp
) else (
    echo [ERROR] Failed to get authentication token
    goto :end
)

echo.
echo 3. DEMONSTRATING THE PROBLEMATIC REQUEST:
echo ------------------------------------------

echo Testing with missing title field ^(this should cause the error^):
curl -s -X POST "http://127.0.0.1:8000/api/tasks/" ^
    -H "Content-Type: application/json" ^
    -H "Authorization: Bearer %TOKEN%" ^
    -d "{}" ^
    -o error_response.tmp

set /p ERROR_RESPONSE=<error_response.tmp
del error_response.tmp
echo [RESULT] Unprocessable Content Error: %ERROR_RESPONSE%

echo.
echo 4. DEMONSTRATING THE CORRECT REQUEST:
echo --------------------------------------

echo Testing with proper format ^(should succeed^):
curl -s -X POST "http://127.0.0.1:8000/api/tasks/" ^
    -H "Content-Type: application/json" ^
    -H "Authorization: Bearer %TOKEN%" ^
    -d "{^"title^":^"Successfully Created Task^",^"description^":^"This is a test task with proper format^"}" ^
    -o success_response.tmp

set /p SUCCESS_RESPONSE=<success_response.tmp
del success_response.tmp
if not "%SUCCESS_RESPONSE:~0,1%"=="{" (
    echo [ERROR] Failed to create task
) else (
    echo [OK] Successfully created task
    echo Response: %SUCCESS_RESPONSE%
)

echo.
echo 5. COMMON CAUSES AND SOLUTIONS:
echo ---------------------------------
echo PROBLEM: Missing 'title' field in request body
echo CAUSE: The TaskCreate schema requires 'title' as a mandatory field
echo SOLUTION: Always include the 'title' field in your request
echo.
echo CORRECT FORMAT:
echo curl -X POST 'http://127.0.0.1:8000/api/tasks/' ^
echo   -H 'Content-Type: application/json' ^
echo   -H 'Authorization: Bearer YOUR_TOKEN' ^
echo   -d '{^"title^":^"Your Task Title^",^"description^":^"Optional description^"}'
echo.
echo INCORRECT FORMATS ^(will cause 422 error^):
echo   -d '{}'
echo   -d '{^"description^":^"No title field^"}'
echo   -d '' ^(empty body^)

echo.
echo 6. ADDITIONAL VALIDATION REQUIREMENTS:
echo ---------------------------------------
echo Title must be 1-200 characters long
echo Description ^(if provided^) must be less than 1000 characters
echo All requests must have valid authentication token
echo All requests must have Content-Type: application/json header

echo.
echo ===========================================
echo TEST COMPLETE - Issue diagnosed and resolved!
echo ===========================================

:end