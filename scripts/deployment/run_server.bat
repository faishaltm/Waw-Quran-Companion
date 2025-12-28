@echo off
REM Change to script directory
cd /d "%~dp0"

echo ========================================
echo   Quran Reading API Server
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found
    echo.
    echo Please create .env file from .env.example:
    echo   copy .env.example .env
    echo.
    echo Then edit .env and add your OPENAI_API_KEY
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing/updating dependencies...
pip install -r requirements.txt --quiet

echo.
echo Starting FastAPI server on http://localhost:8000
echo Interactive docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run server
python -m uvicorn api.main:app --reload --port 8000

pause
