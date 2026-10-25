@echo off
echo ===================================================
echo     MULTIMODAL ATTENDANCE AGENT LAUNCHER
echo ===================================================
echo.

rem Check and activate virtual environment
set VENV_ACTIVATE=
if exist "%~dp0venv\Scripts\activate.bat" (
    set VENV_ACTIVATE="%~dp0venv\Scripts\activate.bat"
) else if exist "%~dp0backend\venv\Scripts\activate.bat" (
    set VENV_ACTIVATE="%~dp0backend\venv\Scripts\activate.bat"
)

echo [1/2] Starting Backend Server on http://localhost:8000 ...
if defined VENV_ACTIVATE (
    start "Backend Server" cmd /k "call %VENV_ACTIVATE% && cd /d "%~dp0backend" && py -3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
) else (
    echo [WARNING] No virtual environment found. Running with global py launcher...
    start "Backend Server" cmd /k "cd /d "%~dp0backend" && py -3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
)
echo    -> Backend will run at: http://localhost:8000
echo.

echo [2/2] Starting Frontend Dashboard on http://localhost:5173 ...
start "Frontend Dashboard" cmd /k "cd /d "%~dp0frontend" && npm run dev"
echo    -> Frontend will run at: http://localhost:5173
echo.
echo ===================================================
echo  Startup complete! Check the 2 opened terminal windows.
echo  Access the dashboard at: http://localhost:5173
echo ===================================================
pause
