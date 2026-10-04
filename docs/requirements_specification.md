# Requirements Specification

## Functional Requirements
- **Equipment tracking**: Track status, type, location, and downtime of all hospital equipment.
- **Downtime tracking**: Accurately log downtime start and calculate duration.
- **Procedure tracking**: Link scheduled clinical procedures to required equipment.
- **Alternative tracking**: Determine if alternative equipment is available for a given down machine.
- **Repair estimates**: Track ETA for repairs.
- **Service impact**: Identify the clinical department affected by the downtime.
- **Priority calculation**: Calculate a Clinical Impact Score to prioritize maintenance over simple downtime duration.
- **Explanation**: Provide human-readable reasons for every system recommendation.
- **Freshness**: Detect and visually flag stale data.
- **Missing-data handling**: Explicitly handle missing data without silent assumptions, triggering fallback workflows.
- **Human review**: Support a human-in-the-loop workflow where recommendations must be verified.
- **Fallback**: Reduce confidence and require manual review when data is missing or stale.
- **Role-based access**: Support tailored views for Biomedical Engineers, Clinical Staff, and Hospital Managers.
- **Audit**: Log all recommendations, overrides, and final decisions.
- **Evaluation**: Measure system alignment with clinical ground truth compared to a downtime-only baseline.

## Non-functional Requirements
- **Privacy**: Implement privacy by design. Minimize sensitive data. No real patient information is used.
- **Explainability**: No black-box AI. The scoring mechanism must be fully transparent and understandable by a non-technical user.
- **Reliability**: System must gracefully handle conflicting or missing data feeds.
- **Usability**: Dashboard must be intuitive for hospital staff under pressure.
- **Security & Authorization**: Gated Role-Based Access Control (RBAC). Clinical Staff cannot override priority directly without engineering or managerial sign-off.
- **Maintainability**: Modular architecture (FastAPI REST API, Streamlit Dashboard, SQLite Engine) for easy future updates.
- **Auditability**: Every decision, override, and clinical expedite request must be traceable with role credentials and timestamps in the audit log.
- **Data quality**: System must actively assess data freshness and output structured, machine-consumable warnings.
- **Evaluation Targets (Honest & Decoupled Calibration)**:
  - **Pearson Correlation ($r$)**: $\ge 0.70$ with independent clinical ground truth (measured: $0.84$).
  - **Triage Precision @ Top 20% Queue**: $\ge 90\%$ (measured: $100.0\%$ zero false highs).
  - **Top-20% Critical Emergency Recall**: $\ge 70\%$ of top-tier hospital emergencies captured (measured: $71.4\%$).
  - **Queue Depth 50% Recall**: $100.0\%$ (full safety coverage of all critical emergencies by 50% queue depth).
