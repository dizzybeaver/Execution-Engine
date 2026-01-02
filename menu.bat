@echo off
REM ============================================
REM EE Main Menu Launcher
REM ============================================
REM
REM This menu provides easy access to all EE interfaces:
REM - CLI: Command-line interface
REM - Dashboard: Web UI and JSON API (port 8080)
REM - Web Console: Browser interface (port 9000)
REM - Flask: Modern web server with SocketIO (port 5000)
REM
REM All interfaces use the Unified Gateway (UG).
REM ============================================

:MENU
cls
echo ============================================
echo EE - Main Menu Launcher
echo ============================================
echo.
echo Select an interface to launch:
echo.
echo [1] Command-Line Interface (CLI)
echo     - Interactive terminal interface
echo     - Execute gateway operations via commands
echo     - List domains, operations, execute routes
echo.
echo [2] Dashboard Server (port 8080)
echo     - Web UI with full-featured interface
echo     - JSON API for programmatic access
echo     - Best for production use
echo.
echo [3] Web Console (port 9000)
echo     - Lightweight browser interface
echo     - Quick operation execution
echo     - Good for development/testing
echo.
echo [4] Flask Server (port 5000)
echo     - Modern web framework
echo     - Real-time updates via SocketIO
echo     - Full-featured web application
echo.
echo [0] Exit
echo.
echo ============================================
set /p choice="Enter your choice [0-4]: "

if "%choice%"=="1" goto CLI
if "%choice%"=="2" goto DASHBOARD
if "%choice%"=="3" goto WEB
if "%choice%"=="4" goto FLASK
if "%choice%"=="0" goto EXIT
goto INVALID

:CLI
cls
echo ============================================
echo EE Command-Line Interface
echo ============================================
echo.
echo Starting CLI...
echo.
echo Common commands:
echo   list-domains              - List all gateway domains
echo   exec config.get           - Execute operation
echo   --json exec config.get    - JSON output format
echo   stats                     - Gateway statistics
echo.
echo Press Ctrl+C to exit CLI
echo ============================================
echo.
"%~dp0launcher\cli\launcher_cli.bat"
pause
goto MENU

:DASHBOARD
cls
echo ============================================
echo EE Dashboard Server
echo ============================================
echo.
echo Starting Dashboard on http://127.0.0.1:8080
echo.
echo Features:
echo   - Web UI at http://127.0.0.1:8080
echo   - JSON API at http://127.0.0.1:8080/api/
echo.
echo Press Ctrl+C to stop server
echo ============================================
echo.
"%~dp0launcher\dashboard\launcher_dashboard.bat"
pause
goto MENU

:WEB
cls
echo ============================================
echo EE Web Console
echo ============================================
echo.
echo Starting Web Console on http://127.0.0.1:9000
echo.
echo Features:
echo   - Browser interface at http://127.0.0.1:9000
echo   - Execute gateway operations
echo   - View operation history
echo.
echo Press Ctrl+C to stop server
echo ============================================
echo.
"%~dp0launcher\web\launcher_web.bat"
pause
goto MENU

:FLASK
cls
echo ============================================
echo EE Flask Server
echo ============================================
echo.
echo Starting Flask server on http://0.0.0.0:5000
echo.
echo Features:
echo   - Modern web interface at http://localhost:5000
echo   - Real-time updates via SocketIO
echo   - Full-featured web application
echo.
echo Press Ctrl+C to stop server
echo ============================================
echo.
"%~dp0launcher\flask\launcher_flask.bat"
pause
goto MENU

:INVALID
cls
echo.
echo ============================================
echo Invalid choice. Please try again.
echo ============================================
echo.
pause
goto MENU

:EXIT
cls
echo.
echo ============================================
echo EE Launcher - Goodbye!
echo ============================================
echo.
timeout /t 2 >nul
exit /b 0
