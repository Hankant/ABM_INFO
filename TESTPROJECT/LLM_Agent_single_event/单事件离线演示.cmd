@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_single_event.ps1" -Mode offline
pause
