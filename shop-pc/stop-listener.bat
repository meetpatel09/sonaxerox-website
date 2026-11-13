@echo off
title Stop Sona Xerox Listener
echo Stopping the Sona Xerox print listener...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*listener.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host ('Stopped process ' + $_.ProcessId) }"
echo.
echo Done. (If nothing was listed above, the listener was not running.)
pause
