@echo off
echo ====================================================================
echo   Multimodal Attendance & Engagement Agent - Environment Setup
echo ====================================================================
echo.

echo [1/3] Creating Python Virtual Environment (venv)...
py -3.12 -m venv venv 2>nul || python -m venv venv
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Failed to create virtual environment. Ensure Python 3.10-3.12 is installed.
    pause
    exit /b 1
)

echo.
echo [2/3] Installing Python Dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install Python dependencies.
    pause
    exit /b 1
)

echo.
echo [3/3] Installing Frontend Dependencies (npm install)...
cd frontend
call npm install
cd ..

echo.
echo ====================================================================
echo   Environment Setup Successful!
echo   1. Copy .env.example to .env and insert your GEMINI_API_KEY.
echo   2. Run start_system.bat to launch both backend and frontend.
echo ====================================================================
pause
