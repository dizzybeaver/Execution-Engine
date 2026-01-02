@echo off
REM EE Flask Server Launcher
REM Launches the EE Flask web server with SocketIO support

echo ============================================
echo EE Flask Web Server Launcher
echo ============================================
echo.

REM Run Python launcher with arguments
python "%~dp0launcher_flask.py" %*

REM Exit with Python exit code
exit /b %ERRORLEVEL%
