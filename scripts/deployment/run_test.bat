@echo off
REM Change to script directory
cd /d "%~dp0"

echo ========================================
echo   Quran Reading API - Test Suite
echo ========================================
echo.

REM Check if server is running
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ERROR: API server is not running
    echo.
    echo Please start the server first:
    echo   run_server.bat
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run test
echo Running test suite...
echo.
python test_api.py

pause
