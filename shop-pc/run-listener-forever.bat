@echo off
title Sona Xerox Print Listener (restarts by itself)
cd /d "%~dp0"
echo Sona Xerox print listener - it restarts automatically if it stops.
echo Close this window to stop it.
echo.
:loop
echo [%date% %time%] Starting listener...
python listener.py
echo.
echo [%date% %time%] Listener stopped. Restarting in 5 seconds...
timeout /t 5 /nobreak >nul
goto loop
