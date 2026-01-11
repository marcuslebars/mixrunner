@echo off
REM Mixrunner GUI Launcher for Windows
REM Double-click this file to launch the GUI

echo ========================================
echo    Mixrunner - Logic Pro Optimizer
echo ========================================
echo.

REM Change to the script's directory
cd /d "%~dp0"

echo Launching Mixrunner GUI...
echo.

REM Try to run with python
python run_gui.py
if errorlevel 1 (
    echo.
    echo Python not found! Trying python3...
    python3 run_gui.py
)

if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from python.org
    echo.
    pause
    exit /b 1
)

pause
