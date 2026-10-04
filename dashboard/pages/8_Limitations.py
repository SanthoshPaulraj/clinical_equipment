import streamlit as st
from utils import inject_custom_styles, render_role_selector

st.set_page_config(page_title="System Boundaries & Limitations | MediPulse AI", page_icon="🛡️", layout="wide")
inject_custom_styles()
role, role_meta = render_role_selector()

st.title("🛡️ System Limitations, Responsible AI & Privacy Disclosures")
st.markdown("""
A foundational pillar of responsible healthcare AI is **uncompromising transparency** regarding system capabilities, 
known boundaries, data privacy architectures, and fail-safe protocols.
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🔒 1. Privacy-by-Design Architecture
    - **Zero Patient Health Information (PHI) Exposure**: The system strictly avoids storing or processing patient names, medical record numbers (MRNs), diagnoses, or demographic data.
    - **Anonymized Operational Abstractions**: Clinical procedures are represented solely via generic operational identifiers (e.g. `PROC-EQ-VEN-029-1`), procedural urgency flags (`EMERGENCY`, `URGENT`, `ROUTINE`), and scheduled duration in minutes.
    - **Decoupled Data Feeds**: The CMMS database only accesses scheduling metadata necessary to quantify service impact, eliminating HIPAA/GDPR clinical exposure vectors.
    - **Role-Based Visibility**: Access to operational telemetry is gated by authenticated staff role credentials.

    ### ⚠️ 2. Algorithmic & Model Boundaries
    - **Linear Composite Scoring**: The current scoring engine relies on a transparent, multi-factorial weighted formulation. While completely explainable, it does not currently model nonlinear compound probabilities (e.g. simultaneous catastrophic failures across redundant power grids).
    - **Single Facility Scope**: The prototype models a single hospital campus (Main Building, Annex, East Wing). Cross-hospital fleet sharing across regional health networks requires additional inter-facility transit modeling.
    - **No Autonomous Diagnostic or Treatment Capability**: This software is explicitly not a Software as a Medical Device (SaMD) diagnostic tool. It cannot assess patient vital signs or dictate clinical care pathways.
    """)

with col2:
    st.markdown("""
    ### 🛑 3. Operational Constraints & Failure Modes
    - **Dependence on EHR & CMMS Telemetry Freshness**: The accuracy of recommendations is fundamentally bounded by the timeliness of upstream schedule and work-order updates. When timestamps exceed 6 hours, the system enforces `VERY_STALE` degradation.
    - **Human Bottleneck Under Surge Crises**: During mass casualty incidents or regional disasters, the mandatory human review verification step must be supported by an expedited crisis override protocol.
    - **Parts Supply Chain Latency**: Repair time estimates reflect technician diagnostic expectations. Unforeseen manufacturer supply chain backorders can lengthen downtime beyond original CMMS estimates.

    ### 📋 4. Responsible AI Governance Checklist
    - **Mandatory Human Accountability**: All final maintenance priority assignments require authorized human engineering or clinical verification.
    - **Tamper-Evident Auditability**: Every override must be accompanied by textual rationale, permanently recorded in the audit log for clinical risk inspection.
    - **Explicit Uncertainty Representation**: Missing or unconfirmed data triggers lower confidence ratings (`LOW` / `MEDIUM`) rather than silent assumptions of safety.
    """)

st.markdown("---")
st.markdown("### 🏁 Deployment & Continuous Verification Roadmap")
st.info("""
**Production Pilot Recommendations:**  
1. Integrate bidirectional HL7/FHIR interfaces with the hospital Electronic Health Record (EHR) for automated procedure cancellation sync.  
2. Connect directly to vendor IoT telemetry gateways (GE Healthcare, Siemens Healthineers, Philips, Dräger) for real-time error code parsing.  
3. Establish a quarterly Clinical-Engineering Safety Committee review to evaluate priority override frequencies and recalibrate departmental urgency multipliers.
""")
