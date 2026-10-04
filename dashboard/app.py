import streamlit as st
from utils import inject_custom_styles, render_role_selector, fetch_json

st.set_page_config(
    page_title="MediPulse AI | Hospital Equipment Downtime Command Center",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_styles()
role, role_meta = render_role_selector()

st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700; color: white;">🏥 Clinical-Impact-Aware Equipment Downtime Command Center</h1>
            <p style="margin: 0.3rem 0 0 0; font-size: 0.95rem; color: #94a3b8;">
                Real-Time Clinical Disruption Triage & Maintenance Decision Support System
            </p>
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 8px; text-align: right;">
            <div style="font-size: 0.75rem; text-transform: uppercase; color: #cbd5e1; letter-spacing: 0.05em;">System Status</div>
            <div style="font-size: 0.95rem; font-weight: 600; color: #4ade80;">● Online & Monitoring</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Prominent Responsible AI & Regulatory Disclaimer
st.warning("""
**Responsible AI Clinical Decision Support Boundary Notice:**  
This system is an operational decision-support tool designed strictly for biomedical maintenance triage and disruption mitigation. 
It **DOES NOT** diagnose patients, prescribe therapy, or execute autonomous clinical workflows. All prioritization decisions remain subject to authorized human engineering and clinical verification.
""")

# Quick KPI Metrics Bar
metrics = fetch_json("dashboard/metrics", default={})
if metrics:
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Total Equipment Fleet", metrics.get("total_equipment", 0))
    with c2:
        st.metric("Equipment Down", metrics.get("equipment_down", 0), delta=f"{metrics.get('critical', 0)} Critical", delta_color="inverse")
    with c3:
        st.metric("Procedures Affected", metrics.get("procedures_affected", 0))
    with c4:
        st.metric("Clinical Services Impacted", metrics.get("services_affected", 0))
    with c5:
        st.metric("Human Reviews Logged", metrics.get("human_reviews_completed", 0), delta="Audit Verified")

st.markdown("---")

# Role-specific contextual orientation
st.markdown(f"### 📋 Welcome, {role}")
if role == "Biomedical Engineer":
    st.info("""
    **Your Active Focus: Technical Triage & Fleet Readiness**  
    - Prioritize pending repair work orders based on verified clinical urgency rather than simple downtime elapsed.
    - Check data freshness and machine warnings before dispatching technician crews.
    - Submit maintenance decisions and document technical override reasons in the Human Review module.
    """)
elif role == "Clinical Staff":
    st.info("""
    **Your Active Focus: Patient Safety & Procedure Continuity**  
    - Track active equipment outages impacting your surgical or ICU schedule.
    - View alternative equipment location and capacity status to divert scheduled patients safely.
    - Submit urgent clinical expedite requests for critical cases requiring immediate technician intervention.
    """)
else:
    st.info("""
    **Your Active Focus: Executive Operations & Governance Oversight**  
    - Monitor cross-department service availability, SLA compliance, and outage distributions.
    - Inspect the comprehensive tamper-evident audit trail of technician decisions and priority overrides.
    - Review the quantitative evaluation report comparing clinical impact triage against legacy downtime sorting.
    """)

st.markdown("### 🧭 System Navigation")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    #### 📊 1. Overview
    High-level KPIs, priority distribution charts, and downtime breakdowns across hospital services and manufacturers.
    """)
    if st.button("Open Overview", key="nav_overview"):
        st.switch_page("pages/1_Overview.py")

with col2:
    st.markdown("""
    #### 🗂️ 2. Prioritization Queue
    Real-time interactive triage queue with clinical impact scoring, freshness indicators, and multi-factor filters.
    """)
    if st.button("Open Prioritization", key="nav_prio"):
        st.switch_page("pages/2_Equipment_Prioritization.py")

with col3:
    st.markdown("""
    #### 👤 3. Human Review
    Mandatory human-in-the-loop review interface with verification checklists, factor evidence, and audit logging.
    """)
    if st.button("Open Human Review", key="nav_review"):
        st.switch_page("pages/3_Human_Review.py")

with col4:
    st.markdown("""
    #### 🗺️ 4. Demo Journeys
    Step-by-step clinical walkthroughs comparing Emergency and Routine patient journeys under both triage systems.
    """)
    if st.button("Open Journeys", key="nav_journeys"):
        st.switch_page("pages/4_Demo_Journeys.py")

col5, col6, col7, col8 = st.columns(4)

with col5:
    st.markdown("""
    #### 📈 5. Evaluation
    Independent empirical evaluation comparing baseline downtime sorting vs. clinical disruption impact scoring.
    """)
    if st.button("Open Evaluation", key="nav_eval"):
        st.switch_page("pages/5_Evaluation.py")

with col6:
    st.markdown("""
    #### ⚠️ 6. Error & Edge Cases
    Interactive simulation testbed for missing alternatives, very stale schedules, and incomplete repair estimates.
    """)
    if st.button("Open Error Analysis", key="nav_error"):
        st.switch_page("pages/6_Error_Analysis.py")

with col7:
    st.markdown("""
    #### 📜 7. Audit Logs
    Comprehensive audit history of all human decisions, overrides, timestamps, and justification records.
    """)
    if st.button("Open Audit Logs", key="nav_audit"):
        st.switch_page("pages/7_Audit_Logs.py")

with col8:
    st.markdown("""
    #### 🛡️ 8. Limitations & Safety
    Transparent disclosure of prototype boundaries, data governance, and responsible AI guardrails.
    """)
    if st.button("Open Limitations", key="nav_limits"):
        st.switch_page("pages/8_Limitations.py")
