@echo off
REM EE Dashboard Launcher
REM Launches the EE Dashboard web interface server

echo ============================================
echo EE Dashboard Server Launcher
echo ============================================
echo.

REM Run Python launcher with arguments
python "%~dp0launcher_dashboard.py" %*

REM Exit with Python exit code
exit /b %ERRORLEVEL%
