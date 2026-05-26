@echo off
title Video Remaster
cd /d "%~dp0"
python src\main.py
if errorlevel 1 (
    echo.
    echo Python was not found. Please install Python 3.7+ from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
)
