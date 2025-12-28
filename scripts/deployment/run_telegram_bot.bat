@echo off
REM Change to script directory
cd /d "%~dp0"

echo ========================================
echo   Quran Reading - Telegram Bot
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found
    echo.
    echo Please create .env file and add TELEGRAM_BOT_TOKEN
    pause
    exit /b 1
)

REM Check if API server is running
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ERROR: FastAPI server is not running
    echo.
    echo Please start the API server first:
    echo   run_server.bat
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo.
echo Starting Telegram Bot...
echo Press Ctrl+C to stop
echo.

python telegram_bot.py

pause
