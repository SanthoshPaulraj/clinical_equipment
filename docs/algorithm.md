# Clinical Impact Algorithm

## Baseline Method
The baseline method for maintenance prioritization relies entirely on the duration of downtime. 
- **Rule**: Longest downtime = Highest priority.
- **Flaw**: Does not account for clinical context. A machine down for 48 hours for a routine procedure is prioritized over a machine down for 2 hours for an emergency surgery.

## Proposed Method: Clinical Impact Engine
The proposed method calculates a Clinical Impact Score (0-100) using a weighted sum of clinical context factors.

### Formula
`Clinical Impact Score = (0.30 × Urgency) + (0.25 × Procedures Affected) + (0.20 × Alternative Risk) + (0.15 × Repair Time) + (0.10 × Service Criticality)`

### Weighting & Normalization
Each component is normalized to a 0-100 scale:
- **Urgency (30%)**: EMERGENCY=100, URGENT=70, ROUTINE=30
- **Procedures Affected (25%)**: ≥3=100, 2=60, 1=30, 0=0
- **Alternative Risk (20%)**: NO Alternative=100, UNKNOWN=50, YES=0
- **Repair Time (15%)**: >24h=100, 8-24h=80, 2-8h=50, <2h=20, Unknown=50
- **Service Criticality (10%)**: Extracted directly from service configuration (e.g. ICU=100)

### Priority Thresholds
The final score is mapped to priority levels:
- **90–100**: CRITICAL
- **75–89**: HIGH
- **50–74**: MEDIUM
- **0–49**: LOW

### Missing Data Handling & Confidence
If data is missing (e.g., Alternative=UNKNOWN), the algorithm does NOT assume a safe default (like Alternative=YES). Instead, it assigns a moderate risk score (50) and drops the system's overall **Confidence** to LOW. This triggers a fallback workflow requiring explicit human verification.
