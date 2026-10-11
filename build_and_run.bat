@echo off
title Multilingual Vision Voice Canvas - Build & Launch
color 0B
echo ======================================================================
echo    MULTILINGUAL VISION VOICE CANVAS - AUTO BUILD & RUN
echo    English | Telugu | Kannada | Hindi
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org and add to PATH.
    pause
    exit /b 1
)

echo [2/3] Installing and verifying required dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies failed to install. Attempting to proceed...
)

echo [3/3] Launching Master Studio Menu...
python main.py
pause
