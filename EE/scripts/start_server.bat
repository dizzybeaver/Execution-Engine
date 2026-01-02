@echo off
REM EE Flask Server Launcher for Windows
REM Starts the EE web interface server

echo Starting EE Flask Server...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)

REM Check if we're in the EE directory
if not exist "ee_config.yaml" (
    echo ERROR: ee_config.yaml not found
    echo Please run this script from the EE directory
    exit /b 1
)

REM Install dependencies if needed
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -q -r requirements.txt

REM Start server
echo.
echo Starting EE Web Interface...
echo Access at: http://localhost:5000
echo Press Ctrl+C to stop
echo.

python run_server.py

pause
