# Clinical-Impact-Aware Equipment Downtime Management and Maintenance Prioritization System

## Problem Statement
A hospital biomedical team maintains medical equipment from many manufacturers. The hospital currently records equipment downtime, but downtime alone does not quantify the potential clinical impact of that equipment being unavailable. A downtime-only system may prioritize equipment that has been down longer, but another piece of equipment down for a shorter time may have much greater potential clinical impact (e.g. emergency procedure scheduled, no alternative available). 

## Objective
The system must help biomedical teams answer: "Which equipment should be prioritized for maintenance to minimize potential clinical disruption?"

## Solution
This project implements a **Clinical-Impact-Aware Equipment Downtime Dashboard**. It calculates a transparent maintenance-priority score based on procedure urgency, procedures affected, alternative availability, repair time, and service criticality.

> **Disclaimer**: Decision-support prototype. Final maintenance and clinical-service decisions require authorized human review. This system MUST NOT diagnose patients, recommend treatment, or make clinical treatment decisions.

## Features
- **Data Ingestion & Validation**: Generates and ingests synthetic hospital data.
- **Freshness & Missing Data Detection**: Explicitly identifies stale or missing data.
- **Clinical Impact Engine**: Calculates a transparent priority score.
- **Explanation Engine**: Generates human-readable reasons for priorities.
- **Role-Based Dashboard**: Streamlit UI for Biomedical Engineers, Clinical Staff, and Hospital Managers.
- **Human-in-the-Loop Workflow**: Biomedical engineer review before final decisions.
- **Audit Logging**: Tracks all decisions and overrides.
- **Evaluation & Metrics**: Compares proposed clinical impact scoring vs baseline downtime-only scoring.

## Architecture & Technology Stack
- **Backend**: Python + FastAPI
- **Dashboard**: Python + Streamlit
- **Data Processing**: Pandas + NumPy
- **Visualization**: Plotly
- **Database**: SQLite + SQLAlchemy
- **Validation**: Pydantic
- **Testing**: Pytest

## Project Structure
```
clinical_equipment_downtime/
├── backend/            # FastAPI application (routes, services, models)
├── dashboard/          # Streamlit dashboard (pages, components)
├── data/               # Synthetic CSV datasets
├── scripts/            # Scripts for data generation, DB seeding, evaluation
├── tests/              # Pytest test suite
├── docs/               # Project documentation
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Setup & Installation

### Windows Environment Setup
Open PowerShell and run the following commands from the project root directory:

1. **Create Virtual Environment**:
   ```powershell
   python -m venv .venv
   ```

2. **Activate Virtual Environment**:
   ```powershell
   .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

### Data & Database Initialization

1. **Generate Synthetic Dataset**:
   ```powershell
   python scripts\generate_dataset.py
   ```
   This generates 100 realistic scenarios in the `data/` directory.

2. **Initialize Database**:
   ```powershell
   python scripts\seed_database.py
   ```
   This creates `hospital_equipment.db` and populates it with the synthetic data.

## Execution

1. **Start FastAPI Backend**:
   Open a new terminal (activate `.venv` first) and run:
   ```powershell
   uvicorn backend.main:app --reload
   ```

2. **Start Streamlit Dashboard**:
   Open a new terminal (activate `.venv` first) and run:
   ```powershell
   streamlit run dashboard\app.py
   ```

## Testing & Evaluation

1. **Run Pytest**:
   ```powershell
   pytest
   ```

2. **Run Evaluation Metrics**:
   ```powershell
   python scripts\run_evaluation.py
   ```

## Documentation
Please refer to the `docs/` folder for comprehensive details:
- `requirements_specification.md`
- `algorithm.md`
- `responsible_ai.md`
- `evaluation_report.md`
- `limitations_report.md`
- `human_review_workflow.md`
- `user_validation.md`
