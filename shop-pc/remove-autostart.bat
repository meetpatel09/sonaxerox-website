@echo off
title Remove Sona Xerox listener auto-start
echo Removing the auto-start task and stopping the listener...
schtasks /Delete /TN "SonaXeroxListener" /F
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*listener.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host ('Stopped process ' + $_.ProcessId) }"
echo.
echo Done. The listener will not start by itself any more.
pause
