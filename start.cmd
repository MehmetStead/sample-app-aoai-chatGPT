@echo off

echo.
echo Checking and installing prerequisites...
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed. Please install Node.js from https://nodejs.org/
    exit /b 1
)

REM Install Angular CLI globally if not already installed
call npm list -g @angular/cli >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Angular CLI globally...
    call npm install -g @angular/cli
)

echo.
echo Starting backend and frontend servers
echo.

REM Start the Python backend using Quart
start cmd /k "python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python -m quart run --host 127.0.0.1 --port 5001"

REM Start the Angular frontend
start cmd /k "cd frontend-angular && npm install && ng serve"

REM Open the application in browser
start http://localhost:4200
