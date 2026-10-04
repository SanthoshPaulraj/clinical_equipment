#!/usr/bin/env bash
set -e

echo "====================================================================="
echo " 🏥 MediPulse AI: Clinical Equipment Downtime System Setup"
echo "====================================================================="
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 not found. Please install Python 3.10+."
    exit 1
fi

PY_VER=$(python3 --version)
echo "[INFO] Detected Python Version: $PY_VER"

# 2. Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[INFO] Creating virtual environment in .venv..."
    python3 -m venv .venv
else
    echo "[INFO] Virtual environment .venv already exists."
fi

# 3. Activate venv
source .venv/bin/activate

# 4. Install dependencies
echo "[INFO] Upgrading pip and installing requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Seed database
echo "[INFO] Seeding SQLite database from CSV datasets..."
python scripts/seed_database.py

# 6. Run test suite
echo "[INFO] Executing comprehensive pytest suite..."
python -m pytest tests/ -v

# 7. Run evaluation benchmark
echo "[INFO] Executing independent clinical disruption benchmark..."
python scripts/run_evaluation.py

echo ""
echo "====================================================================="
echo " ✅ Setup Complete! All tests passed and benchmark executed."
echo "====================================================================="
echo " To start the application:"
echo "   make run-all"
echo "   OR"
echo "   ./run.sh"
echo ""
