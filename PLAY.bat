@echo off
title PyCraft Launcher - Quick Start
color 0A

echo ========================================
echo    PYCRAFT LAUNCHER
echo ========================================
echo.

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo First time setup detected...
    echo Installing dependencies automatically...
    echo.
    python install_and_play.py
    exit /b
)

REM Launch directly if already installed
echo Starting launcher...
streamlit run launcher.py --server.headless true

pause
