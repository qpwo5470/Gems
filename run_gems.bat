@echo off
echo ============================================================
echo Gems Station Launcher
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Show Python version
echo Python version:
python --version
echo.

REM Check if running from the correct directory
if not exist "google_gems.py" (
    echo ERROR: google_gems.py not found in current directory
    echo Please run this script from the Gems project directory
    pause
    exit /b 1
)

REM Set environment variables for better compatibility
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=1

REM Run the simplified launcher
echo Starting Gems Station...
echo.
python run_gems_windows.py

REM If Python script exits with error, pause
if %errorlevel% neq 0 (
    echo.
    echo Script exited with error code: %errorlevel%
    pause
)