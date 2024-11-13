@echo off
:: Check if the script is already running in a new window
if "%1"=="new_window" goto :continue

:: If not, open a new Command Prompt and rerun this script
start cmd /k "%~0 new_window"
exit

:continue
:: Script continues from here in the new window

echo.
echo *** DON'T CLOSE ANY TERMINAL! ***
echo If the terminals are closed, then the website won't be visible.
echo.

:: Ask the user if this is their first time running the script
set /p firstTime="Are you running this for the first time? (y/n): "

:: Change to the frontend directory
cd frontend || (echo Failed to change to frontend directory & exit /b)

:: If the user says yes, run npm install
if /i "%firstTime%"=="y" (
    echo Installing dependencies...
    npm install || (echo npm install failed & exit /b)
    
    echo Starting the development server...
    start cmd /k "npm run dev -- --host"

    :: Wait for a few seconds to let the development server start
    timeout /t 5
    start "" "http://localhost:5173"
) else (
    :: If the user says no, just start the development server
    echo Starting the development server...
    start cmd /k "npm run dev -- --host"

    :: Wait for a few seconds to let the server start
    timeout /t 2
    start "" "http://localhost:5173"
)

exit
