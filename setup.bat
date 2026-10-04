@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo  🏥 MediPulse AI: Clinical Equipment Downtime System Setup
echo =====================================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH. Please install Python 3.10 or higher.
    exit /b 1
)

for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PY_VER=%%I
echo [INFO] Detected Python Version: %PY_VER%

:: 2. Create or verify virtual environment
if not exist ".venv" (
    echo [INFO] Creating Python virtual environment in .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
) else (
    echo [INFO] Virtual environment .venv already exists.
)

:: 3. Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

:: 4. Install dependencies
echo [INFO] Installing / verifying dependencies from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    exit /b 1
)

:: 5. Generate and seed database
echo [INFO] Generating synthetic hospital dataset and seeding SQLite database...
python scripts\seed_database.py
if %errorlevel% neq 0 (
    echo [ERROR] Database seeding failed.
    exit /b 1
)

:: 6. Run test suite
echo [INFO] Running test suite...
python -m pytest tests/ -v
if %errorlevel% neq 0 (
    echo [ERROR] Tests failed!
    exit /b 1
)

:: 7. Run evaluation benchmark
echo [INFO] Running independent clinical disruption benchmark...
python scripts\run_evaluation.py

echo.
echo =====================================================================
echo  ✅ Setup Complete! All 22 tests passed and benchmark executed.
echo =====================================================================
echo.
echo  To start the application:
echo    1. Start Backend:    uvicorn backend.main:app --reload --port 8000
echo    2. Start Dashboard:  streamlit run dashboard/app.py --server.port 8501
echo    OR simply run:       run.bat
echo.
pause
