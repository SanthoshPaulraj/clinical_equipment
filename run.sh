#!/usr/bin/env bash
set -e

echo "====================================================================="
echo " 🏥 Starting MediPulse AI Backend & Command-Center Dashboard"
echo "====================================================================="
echo ""

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "Starting FastAPI backend on http://localhost:8000 ..."
echo "Starting Streamlit dashboard on http://localhost:8501 ..."
echo ""

python3 -c "import subprocess, sys; p1 = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'backend.main:app', '--port', '8000', '--reload']); p2 = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'dashboard/app.py', '--server.port', '8501']); p1.wait(); p2.wait()"
