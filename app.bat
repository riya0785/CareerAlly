@echo off
:: Check if the script is already running in a new window
if "%1"=="new_window" goto :continue

:: If not, open a new Command Prompt and rerun this script
start cmd /k "%~0 new_window"
exit

:continue

echo.
echo *** DON'T CLOSE ANY TERMINAL! ***
echo Running As Android App
echo.
cd frontend
timeout /t 2
start cmd /k "npx cap copy"
timeout /t 2
start cmd /k "npx cap sync"
timeout /t 2
start cmd /k "npx cap open android"
