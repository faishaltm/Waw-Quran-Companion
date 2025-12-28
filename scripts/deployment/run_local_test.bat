@echo off
REM Change to script directory
cd /d "%~dp0"

echo ====================================
echo Quran Verse Analysis - Local Testing
echo ====================================
echo.

REM Check if argument provided
if "%~1"=="" (
    echo Usage: run_local_test.bat ^<verse_range^>
    echo Example: run_local_test.bat 68:1-10
    echo Example: run_local_test.bat 2:255
    echo.
    pause
    exit /b
)

python test_verse_analysis_local.py %1

pause
