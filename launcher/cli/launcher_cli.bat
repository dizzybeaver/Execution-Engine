@echo off
REM EE CLI Launcher
REM Launches the EE Command-Line Interface

echo ============================================
echo EE Command-Line Interface Launcher
echo ============================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0

REM Run Python launcher
python "%SCRIPT_DIR%launcher_cli.py" %*

REM Exit with Python exit code
exit /b %ERRORLEVEL%
