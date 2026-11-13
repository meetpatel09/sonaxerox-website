@echo off
title Sona Xerox Print Listener
cd /d "%~dp0"
echo Starting Sona Xerox print listener...
python listener.py
echo.
echo Listener stopped. Press any key to close.
pause >nul
