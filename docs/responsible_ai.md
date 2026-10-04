# Responsible AI and Ethical Considerations

## 1. No Automated Clinical Decisions
This system operates strictly within a **decision-support** boundary for equipment maintenance. It does NOT diagnose patients, recommend treatments, or automate clinical care decisions.

## 2. Human Oversight (Human-in-the-Loop)
The system never automatically executes maintenance prioritization without human review. A Biomedical Engineer must review the system's recommendation, verify the underlying data, and explicitly accept or override the decision.

## 3. Explainability
The system eschews "black-box" machine learning models in favor of a transparent, rule-based algorithm. Every priority score is accompanied by human-readable explanations detailing exactly which factors increased or decreased the score.

## 4. Data Minimization & Privacy
The system uses **Privacy by Design**. It requires only operational metadata (procedure type, urgency, equipment ID). It explicitly strips and ignores patient names, demographics, and clinical histories to minimize the risk of PHI (Protected Health Information) exposure.

## 5. Handling Missing & Stale Data
AI systems often fail dangerously when data is missing or stale. This system implements an explicit **Fallback Engine**:
- **Stale-data handling**: Identifies data older than thresholds and generates visual warnings, reducing system confidence.
- **Missing-data handling**: Explicitly handles unknowns without unsafe assumptions (e.g., an unknown alternative is treated as a risk, not an assurance).

## 6. Auditability
Every human review, acceptance, and override is logged with a timestamp, user role, and reasoning. This ensures full accountability for maintenance prioritization decisions.
