@echo off
title Install Sona Xerox listener auto-start
cd /d "%~dp0"
echo.
echo This makes Windows check EVERY MINUTE that the print listener is running,
echo and start it (invisibly) if it is not. Works after restart, crash or accidental close.
echo.
schtasks /Create /TN "SonaXeroxListener" /TR "wscript.exe \"%~dp0keep-listener-running.vbs\"" /SC MINUTE /MO 1 /F
if errorlevel 1 (
  echo.
  echo FAILED. Right-click this file and choose "Run as administrator", then try again.
  pause
  exit /b 1
)
schtasks /Run /TN "SonaXeroxListener" >nul
echo.
echo DONE. The listener is now running in the background and will always come back.
echo Check: Task Manager -^> "pythonw.exe", and the end of listener.log.
echo To switch this off, run remove-autostart.bat
echo.
pause
