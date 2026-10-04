import streamlit as st
from utils import inject_custom_styles, render_role_selector, fetch_json

st.set_page_config(page_title="Demonstration Journeys | MediPulse AI", page_icon="🗺️", layout="wide")
inject_custom_styles()
role, role_meta = render_role_selector()

st.title("🗺️ Clinical Patient Journeys & Human Review Points")
st.markdown("""
This module demonstrates how the **Clinical Impact Engine** resolves the fatal flaw of elapsed downtime sorting. 
Two journeys of vastly different urgency are compared side-by-side to illustrate real-world disruption avoidance.
""")

tab_emergency, tab_routine, tab_review_points = st.tabs([
    "🚨 Journey A: Emergency ICU Ventilator Outage",
    "🩺 Journey B: Routine Outpatient ECG Outage",
    "🛡️ Documented Human Review Decision Points"
])

with tab_emergency:
    st.markdown("### 🚨 Emergency Clinical Journey: Severe Trauma Patient Awaiting ICU Ventilator")
    
    col_em_ctx, col_em_cmp = st.columns([1, 1.2])
    with col_em_ctx:
        st.markdown("""
        <div style="background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 1.2rem;">
            <h4 style="color: #991b1b; margin-top:0;">Clinical Scenario Profile</h4>
            <ul>
                <li><strong>Equipment:</strong> Dräger Evita V800 Ventilator (<code>EQ-VEN-029</code>)</li>
                <li><strong>Location:</strong> Intensive Care Unit (Main Building, Floor 3)</li>
                <li><strong>Elapsed Downtime:</strong> <strong>1.2 hours</strong> (Recent failure)</li>
                <li><strong>Pending Procedure:</strong> Invasive Mechanical Ventilation for Acute Respiratory Failure</li>
                <li><strong>Procedure Urgency:</strong> <span style="background-color:#ef4444; color:white; padding:2px 6px; border-radius:4px; font-weight:700;">EMERGENCY</span></li>
                <li><strong>Scheduled Start:</strong> In 35 minutes</li>
                <li><strong>Alternative Hardware:</strong> <strong>NONE AVAILABLE</strong> (ICU fleet fully allocated)</li>
                <li><strong>Estimated Repair Time:</strong> 4.5 hours (requires diaphragm valve replacement)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_em_cmp:
        st.markdown("#### System Triage Comparison")
        st.markdown("""
        | Factor | ⏳ Status-Quo Baseline (Downtime Hours Only) | 🏥 Proposed System (Clinical Impact Engine) |
        | :--- | :--- | :--- |
        | **Triage Rank** | **#58 out of 70** (Bottom Quartile) | **#1 out of 70** (Top Priority) |
        | **Calculated Score** | **1.7 / 100** (Normalized Downtime) | **94.5 / 100** (CRITICAL Impact) |
        | **Clinical Outcome** | **Catastrophic Care Delay:** Technician dispatched to routine machines that were down longer. Patient emergency delayed. | **Disruption Avoided:** Senior BMET dispatched in 5 minutes with replacement valve. ICU room ready on time. |
        | **Data Confidence** | Ignored (Assumes downtime is truth) | **HIGH** (All telemetry and schedules verified fresh) |
        """)

    st.markdown("---")
    st.markdown("#### ⏱️ Step-by-Step Clinical Workflow Progression")
    
    steps = [
        ("08:00 AM", "Ventilator Telemetry Alarm", "Ventilator sensor fails calibration. Ingested into database with status DOWN. Downtime clock starts.", "Freshness Engine verifies timestamp (<1h)."),
        ("08:15 AM", "Emergency Trauma Admission", "EHR scheduling interface links emergency trauma case requiring ventilator in ICU Bed 4.", "Urgency score jumps to 100 (EMERGENCY)."),
        ("08:16 AM", "Automated Impact Scoring", "Engine detects No Alternative in ICU + Critical Service (ICU) + Emergency procedure.", "Impact score calculated: 94.5 (CRITICAL). Elevated to Work Order #1."),
        ("08:20 AM", "Human Review Point 1 & 4", "Lead BMET Marcus Vance inspects dashboard, verifies parts in stock, and validates work order.", "BMET confirms 4-point verification checklist."),
        ("08:25 AM", "Technician Dispatched", "BMET team dispatched to ICU with pre-pulled diaphragm replacement kit.", "Audit log records technician dispatch and acceptance."),
        ("08:50 AM", "Repair Complete & Patient Safe", "Ventilator calibrated and tested. Machine returned to AVAILABLE 10 minutes before patient arrival.", "Zero clinical disruption; trauma case proceeded without delay.")
    ]
    
    for time_str, title_str, desc_str, sys_str in steps:
        st.markdown(f"""
        <div style="display: flex; margin-bottom: 0.8rem; border-left: 3px solid #ef4444; padding-left: 1rem;">
            <div style="min-width: 90px; font-weight: 700; color: #991b1b;">{time_str}</div>
            <div style="flex-grow: 1;">
                <strong style="color: #0f172a;">{title_str}</strong> — {desc_str}<br>
                <span style="font-size: 0.8rem; color: #0284c7; font-weight:600;">System Action: {sys_str}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab_routine:
    st.markdown("### 🩺 Routine Clinical Journey: Outpatient ECG Monitor with Available Alternative")
    
    col_rt_ctx, col_rt_cmp = st.columns([1, 1.2])
    with col_rt_ctx:
        st.markdown("""
        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 1.2rem;">
            <h4 style="color: #166534; margin-top:0;">Clinical Scenario Profile</h4>
            <ul>
                <li><strong>Equipment:</strong> GE Healthcare MAC 2000 ECG Cart (<code>EQ-ECG-028</code>)</li>
                <li><strong>Location:</strong> Outpatient Cardiology Clinic (Annex, Floor 1)</li>
                <li><strong>Elapsed Downtime:</strong> <strong>48.2 hours</strong> (Down over weekend)</li>
                <li><strong>Pending Procedure:</strong> Routine Pre-Operative Clearance ECG</li>
                <li><strong>Procedure Urgency:</strong> <span style="background-color:#22c55e; color:white; padding:2px 6px; border-radius:4px; font-weight:700;">ROUTINE</span></li>
                <li><strong>Scheduled Start:</strong> Tomorrow afternoon</li>
                <li><strong>Alternative Hardware:</strong> <strong>3 CARTS AVAILABLE</strong> in adjacent exam rooms with verified capacity</li>
                <li><strong>Estimated Repair Time:</strong> 1.5 hours (lead replacement)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_rt_cmp:
        st.markdown("#### System Triage Comparison")
        st.markdown("""
        | Factor | ⏳ Status-Quo Baseline (Downtime Hours Only) | 🏥 Proposed System (Clinical Impact Engine) |
        | :--- | :--- | :--- |
        | **Triage Rank** | **#4 out of 70** (Top 5 Priority!) | **#62 out of 70** (Low Priority) |
        | **Calculated Score** | **66.9 / 100** (Artificially Inflated) | **38.2 / 100** (LOW Clinical Impact) |
        | **Operational Impact** | **Misallocated Resources:** Technician sent across hospital campus to repair a non-urgent machine while urgent OR equipment languished. | **Optimized Throughput:** Work order batched for routine end-of-shift maintenance. Emergency equipment prioritized. |
        | **Patient Safety** | Zero clinical impact (alternatives were plentiful) | Patient easily redirected to exam room 3; zero wait time. |
        """)

    st.markdown("---")
    st.markdown("#### ⏱️ Step-by-Step Clinical Workflow Progression")
    
    rt_steps = [
        ("Friday 04:00 PM", "Cable Wear Detected", "Nurse notes fraying lead on outpatient ECG. Logs maintenance request before weekend.", "Downtime counter starts accumulating hours."),
        ("Monday 08:00 AM", "Status-Quo Distortion", "Legacy CMMS displays 48 hours of downtime. Ranks as priority #4 in morning dispatch queue.", "Legacy system creates false urgency due to elapsed time alone."),
        ("Monday 08:01 AM", "Clinical Impact Triage", "Engine correlates Routine urgency (30.0) + Alternative available (0.0) + Short repair (20.0).", "Calculates score 38.2 (LOW Priority). Placed at slot #62."),
        ("Monday 08:15 AM", "Human Review Point 3 & 6", "BMET confirms 3 identical ECG units ready in Annex. Agrees with LOW priority rating.", "Work order queued for late afternoon maintenance sweep."),
        ("Monday 04:30 PM", "Routine Repair Executed", "Technician replaces cable during scheduled rounds without disrupting active surgeries.", "Audit log records successful closeout with zero patient delays.")
    ]
    
    for time_str, title_str, desc_str, sys_str in rt_steps:
        st.markdown(f"""
        <div style="display: flex; margin-bottom: 0.8rem; border-left: 3px solid #22c55e; padding-left: 1rem;">
            <div style="min-width: 140px; font-weight: 700; color: #166534;">{time_str}</div>
            <div style="flex-grow: 1;">
                <strong style="color: #0f172a;">{title_str}</strong> — {desc_str}<br>
                <span style="font-size: 0.8rem; color: #0284c7; font-weight:600;">System Action: {sys_str}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab_review_points:
    st.markdown("### 🛡️ Documented Human Review Decision Points")
    st.markdown("""
    The clinical operations and biomedical engineering leadership formally approved **8 mandatory human decision checkpoints** 
    governing every stage of the lifecycle:
    """)
    
    review_pts = [
        ("RP-1", "Telemetry & Status Verification", "BMET confirms device is genuinely inoperable (not rebooting or in calibration mode).", "Biomedical Engineer"),
        ("RP-2", "EHR Schedule & Urgency Confirmation", "Clinical nurse coordinator verifies active patient bookings and urgency flags.", "Clinical Staff / Nurse"),
        ("RP-3", "Physical Alternative Readiness Check", "Confirmation that backup device is powered, calibrated, and physically accessible.", "Biomedical / Nurse"),
        ("RP-4", "Repair Feasibility & Parts Verification", "BMET checks local inventory for required spare parts and technician skill set.", "Biomedical Engineer"),
        ("RP-5", "Data Integrity Fallback Gate", "Mandatory dual sign-off enforced whenever confidence is LOW or data is VERY STALE.", "BMET + Clinical Lead"),
        ("RP-6", "Priority Sign-Off / Override Decision", "Formal agreement or override of automated recommendation with recorded role.", "Authorized BMET / Manager"),
        ("RP-7", "Mandatory Justification Logging", "Structured textual justification permanently written to tamper-evident audit log.", "System Enforcement"),
        ("RP-8", "Post-Repair Return-to-Service Test", "Electrical safety and diagnostic functional check prior to clearing machine to AVAILABLE.", "Biomedical Engineer")
    ]
    
    df_rp = pd.DataFrame(review_pts, columns=["Code", "Review Checkpoint", "Operational Protocol", "Accountable Stakeholder"])
    st.dataframe(df_rp, use_container_width=True, hide_index=True)
