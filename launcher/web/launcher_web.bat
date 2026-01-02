@echo off
REM EE Web Console Launcher
REM Launches the EE Web Console server

echo ============================================
echo EE Web Console Launcher
echo ============================================
echo.

REM Run Python launcher with arguments
python "%~dp0launcher_web.py" %*

REM Exit with Python exit code
exit /b %ERRORLEVEL%
