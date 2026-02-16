@echo off
title PyCraft Launcher - Auto Install
color 0A

echo ========================================
echo    PYCRAFT LAUNCHER - AUTO INSTALLER
echo ========================================
echo.

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)
python --version
echo.

echo [2/3] Installing required packages...
echo This may take a minute...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo WARNING: Some packages may have failed to install
    echo Trying without --quiet flag...
    python -m pip install -r requirements.txt
)
echo.

echo [3/3] Launching PyCraft...
echo.
echo ========================================
echo    STARTING LAUNCHER...
echo ========================================
echo.

streamlit run launcher.py --server.headless true

pause
