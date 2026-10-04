.PHONY: setup install seed test eval run-backend run-dashboard run-all clean help

PYTHON ?= python
PIP ?= pip
UVICORN ?= uvicorn
STREAMLIT ?= streamlit

help:
	@echo "=================================================================="
	@echo "🏥 MediPulse AI - Clinical Equipment Downtime Triage Engine"
	@echo "=================================================================="
	@echo "Available commands:"
	@echo "  make setup          - Initialize environment, install deps, seed DB, run tests"
	@echo "  make install        - Install requirements.txt"
	@echo "  make seed           - Generate synthetic cohort and seed SQLite database"
	@echo "  make test           - Run full test suite with pytest"
	@echo "  make eval           - Run independent clinical disruption benchmark"
	@echo "  make run-backend    - Start FastAPI REST API server on port 8000"
	@echo "  make run-dashboard  - Start Streamlit command-center on port 8501"
	@echo "  make run-all        - Launch both backend and dashboard together"
	@echo "  make clean          - Remove temporary files and pycache"
	@echo "=================================================================="

setup: install seed test eval
	@echo "✅ System setup complete and validated!"

install:
	$(PIP) install -r requirements.txt

seed:
	$(PYTHON) scripts/generate_dataset.py
	$(PYTHON) scripts/seed_database.py

test:
	$(PYTHON) -m pytest tests/ -v

eval:
	$(PYTHON) scripts/run_evaluation.py

run-backend:
	$(UVICORN) backend.main:app --host 0.0.0.0 --port 8000 --reload

run-dashboard:
	$(STREAMLIT) run dashboard/app.py --server.port 8501

run-all:
	@echo "Starting FastAPI backend and Streamlit dashboard..."
	@python -c "import subprocess, sys; p1 = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'backend.main:app', '--port', '8000']); p2 = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'dashboard/app.py', '--server.port', '8501']); p1.wait(); p2.wait()"

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned cache and temporary files."
