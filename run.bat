@echo off
echo =====================================================================
echo  🏥 Starting MediPulse AI Backend & Command-Center Dashboard
echo =====================================================================
echo.

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo Starting FastAPI backend on http://localhost:8000 ...
echo Starting Streamlit dashboard on http://localhost:8501 ...
echo.

python -c "import subprocess, sys; p1 = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'backend.main:app', '--port', '8000', '--reload']); p2 = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'dashboard/app.py', '--server.port', '8501']); p1.wait(); p2.wait()"
