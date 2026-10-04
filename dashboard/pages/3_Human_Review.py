import streamlit as st
import pandas as pd
from utils import inject_custom_styles, render_role_selector, fetch_json, post_json

st.set_page_config(page_title="Human-in-the-Loop Review | MediPulse AI", page_icon="👤", layout="wide")
inject_custom_styles()
role, role_meta = render_role_selector()

st.title("👤 Human-in-the-Loop Decision & Verification Workflow")
st.markdown("""
**Mandatory Clinical Safety Protocol**: Automated scores represent decision support only. 
Final maintenance dispatch and queue prioritization require authorized human verification and sign-off.
""")

# Ensure an equipment item is selected
if "review_equipment_id" not in st.session_state:
    st.warning("⚠️ No equipment currently selected. Please select a work order from the Prioritization Queue or choose below:")
    down_equipment = fetch_json("equipment", default=[])
    down_ids = [e["equipment_id"] for e in down_equipment if e.get("status") == "DOWN"] if down_equipment else []
    if down_ids:
        chosen = st.selectbox("Select Equipment ID to review:", down_ids)
        if st.button("Load Selected Equipment"):
            st.session_state["review_equipment_id"] = chosen
            st.rerun()
    st.stop()

eq_id = st.session_state["review_equipment_id"]
st.subheader(f"Reviewing Work Order: `{eq_id}`")

# Fetch full context from backend
eq = fetch_json(f"equipment/{eq_id}")
impact = fetch_json(f"impact/{eq_id}")
procedures = fetch_json(f"procedures?equipment_id={eq_id}", default=[])

if not eq or not impact:
    st.error(f"Could not load details for equipment {eq_id}. Please ensure backend API is running.")
    st.stop()

# Layout: Left column Equipment Context & Freshness, Right column Score & Explanation
col_left, col_right = st.columns([1.1, 1.3])

with col_left:
    st.markdown("### 🔧 Equipment & Fleet Context")
    st.markdown(f"""
    - **Modality / Type:** `{eq.get('equipment_type')}`
    - **Manufacturer:** `{eq.get('manufacturer')}` ({eq.get('model')})
    - **Department / Location:** `{eq.get('department')}`
    - **Clinical Service ID:** `{eq.get('service')}`
    - **Operational Status:** <span style="color:#ef4444; font-weight:700;">{eq.get('status')}</span>
    - **Elapsed Downtime:** **{eq.get('downtime_hours', 0):.1f} hours**
    - **Downtime Began:** `{eq.get('downtime_start', 'N/A')}`
    """, unsafe_allow_html=True)

    st.markdown("### 🕒 Operational Data Freshness")
    freshness = impact.get("freshness", {})
    f_cols = st.columns(4)
    badges = {
        "FRESH": "badge-fresh",
        "STALE": "badge-stale",
        "VERY_STALE": "badge-very-stale",
        "MISSING": "badge-missing"
    }
    
    stream_keys = [("Equipment", "equipment"), ("Procedures", "procedures"), ("Alternative", "alternative"), ("Repair", "repair")]
    for col, (label, key) in zip(f_cols, stream_keys):
        val = freshness.get(key, "MISSING")
        css_class = badges.get(val, "badge-missing")
        col.markdown(f"**{label}**<br><span class='{css_class}'>{val}</span>", unsafe_allow_html=True)

    # Machine-consumable warnings display
    machine_warnings = impact.get("machine_warnings", [])
    if machine_warnings:
        st.markdown("### ⚠️ Active Machine Warnings (Automated Guardrails)")
        for mw in machine_warnings:
            sev_color = "#ef4444" if mw.get("severity") in ["CRITICAL", "HIGH"] else "#f97316"
            st.markdown(f"""
            <div style="background-color: #fef2f2; border-left: 4px solid {sev_color}; padding: 0.6rem 0.9rem; border-radius: 4px; margin-bottom: 0.5rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong style="color: {sev_color}; font-size: 0.8rem;">[{mw.get('code')}] {mw.get('severity')}</strong>
                    <span style="font-size: 0.7rem; color: #64748b;">Field: {mw.get('field')}</span>
                </div>
                <div style="font-size: 0.85rem; color: #1e293b; margin: 0.2rem 0;">{mw.get('message')}</div>
                <div style="font-size: 0.75rem; color: #0284c7; font-weight:600;">➔ Action Required: {mw.get('action_required')}</div>
            </div>
            """, unsafe_allow_html=True)

    # Scheduled procedures table
    st.markdown("### 📅 Scheduled Patient Procedures")
    if procedures:
        p_df = pd.DataFrame(procedures)[["procedure_id", "procedure_type", "urgency", "scheduled_time", "duration_minutes"]]
        st.dataframe(p_df, use_container_width=True, height=160)
    else:
        st.info("No active scheduled procedures linked to this machine in the EHR interface.")

with col_right:
    st.markdown("### 🎯 Clinical Impact Recommendation")
    
    score = impact.get("score", 0.0)
    priority = impact.get("priority", "UNKNOWN")
    confidence = impact.get("confidence", "UNKNOWN")
    
    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("Clinical Impact Score", f"{score:.1f} / 100")
    
    prio_colors = {"CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#eab308", "LOW": "#22c55e"}
    p_color = prio_colors.get(priority, "#64748b")
    
    c_m2.markdown(f"""
    <div style="margin-top: 0.5rem;">
        <div style="font-size: 0.8rem; color: #64748b;">System Recommendation</div>
        <div style="font-size: 1.5rem; font-weight: 800; color: {p_color};">{priority}</div>
    </div>
    """, unsafe_allow_html=True)
    
    conf_colors = {"HIGH": "#22c55e", "MEDIUM": "#eab308", "LOW": "#ef4444"}
    c_color = conf_colors.get(confidence, "#64748b")
    c_m3.markdown(f"""
    <div style="margin-top: 0.5rem;">
        <div style="font-size: 0.8rem; color: #64748b;">Data Confidence</div>
        <div style="font-size: 1.5rem; font-weight: 800; color: {c_color};">{confidence}</div>
    </div>
    """, unsafe_allow_html=True)

    # Fallback alert banner if active
    explanation = impact.get("explanation", {})
    if explanation.get("fallback_triggered"):
        st.markdown("""
        <div class="fallback-alert">
            <strong style="color: #b91c1c;">⚠️ FALLBACK PROTOCOL ACTIVE</strong><br>
            <span style="font-size: 0.825rem; color: #7f1d1d;">
                Data feeds contain missing, very stale, or unconfirmed attributes. Automated confidence is degraded. 
                Dual biomedical and clinical verification is required before work order closeout.
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 🧠 Transparent Factor-Level Explanation")
    st.markdown("*Review the individual clinical and operational variables driving this recommendation:*")
    
    for inc in explanation.get("factors_increasing", []):
        st.markdown(f"🔺 <span style='color: #b91c1c; font-weight:500;'>{inc}</span>", unsafe_allow_html=True)
    for dec in explanation.get("factors_decreasing", []):
        st.markdown(f"🔽 <span style='color: #15803d; font-weight:500;'>{dec}</span>", unsafe_allow_html=True)
    for mw in explanation.get("missing_data_warnings", []):
        st.markdown(f"⚠️ <span style='color: #d97706;'>Missing: {mw}</span>", unsafe_allow_html=True)
    for sw in explanation.get("stale_data_warnings", []):
        st.markdown(f"🕒 <span style='color: #d97706;'>Stale: {sw}</span>", unsafe_allow_html=True)

st.markdown("---")

# 4. Gated Role-Based Review Form
st.markdown(f"### ✍️ Final Maintenance Decision — Active Role: `{role}`")

if role == "Clinical Staff":
    st.info("""
    **Clinical Staff Mode**: You are viewing this work order from the patient care perspective. 
    You may verify patient procedure urgency and submit an urgent clinical expedite request with patient risk rationale.
    """)
    with st.form("clinical_expedite_form"):
        st.markdown("#### Clinical Urgency Verification Checklist")
        chk_sched = st.checkbox("I have confirmed the pending patient schedule with the charge nurse.")
        chk_patient = st.checkbox("I have verified that patient care/surgical prep is active.")
        chk_alt = st.checkbox("I have checked adjacent rooms and confirmed alternative machine capacity.")
        
        request_level = st.selectbox("Requested Clinical Urgency:", ["CRITICAL", "HIGH", "MEDIUM", "LOW"], index=["CRITICAL", "HIGH", "MEDIUM", "LOW"].index(priority))
        clinical_notes = st.text_area("Clinical Notes & Patient Risk Details (e.g. ICU patient unstable, surgeon waiting):", required=True)
        
        btn_submit = st.form_submit_button("Submit Clinical Expedite Request", type="primary")
        if btn_submit:
            if not clinical_notes.strip():
                st.error("Please provide clinical risk details justifying the request.")
            else:
                payload = {
                    "equipment_id": eq_id,
                    "recommendation": priority,
                    "human_decision": request_level,
                    "reviewer_role": "Clinical Staff",
                    "review_comments": clinical_notes,
                    "override_reason": f"Clinical Urgency Request by Nursing Lead: {request_level}"
                }
                status, res = post_json("review", payload)
                if status == 200:
                    st.success("✅ Clinical expedite request logged and sent to Biomedical Engineering triage queue!")
                    st.balloons()
                else:
                    st.error(f"Error submitting request: {res.get('detail')}")

elif role == "Biomedical Engineer":
    st.info("""
    **Biomedical Engineer Mode**: Authorized to triage technical work orders, dispatch repair technicians, and execute formal priority decisions.
    """)
    with st.form("bmet_review_form"):
        st.markdown("#### Technical & Clinical Verification Checklist")
        c_chk1, c_chk2 = st.columns(2)
        with c_chk1:
            chk1 = st.checkbox("1. Physical Equipment Status verified (Unit confirmed DOWN).")
            chk2 = st.checkbox("2. Procedure Schedule & Urgency checked with care unit.")
        with c_chk2:
            chk3 = st.checkbox("3. Alternative Equipment fleet status & capacity verified.")
            chk4 = st.checkbox("4. Repair ETA & Manufacturer replacement parts confirmed.")
            
        st.markdown("#### Final Maintenance Priority Decision")
        p_options = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        decision = st.selectbox("Assign Final Work Order Priority:", p_options, index=p_options.index(priority))
        
        override_reason = ""
        is_override = (decision != priority)
        if is_override:
            st.warning("⚠️ **Override Detected**: You are modifying the automated recommendation. A formal engineering justification is legally required.")
            override_reason = st.text_area(
                "Mandatory Justification for Priority Override:", 
                placeholder="Explain the technical or clinical factor not captured by the automated engine (e.g. parts arriving tomorrow morning, secondary backup located in East Wing)."
            )
            
        tech_comments = st.text_area("Technician Work Order Notes & Dispatch Instructions:")
        
        btn_submit = st.form_submit_button("Sign & Submit Maintenance Work Order", type="primary")
        if btn_submit:
            if not (chk1 and chk2 and chk3 and chk4):
                st.error("⚠️ All 4 verification checklist items must be confirmed before submitting.")
            elif is_override and not override_reason.strip():
                st.error("⚠️ Mandatory justification is required when overriding automated priority.")
            else:
                payload = {
                    "equipment_id": eq_id,
                    "recommendation": priority,
                    "human_decision": decision,
                    "reviewer_role": "Biomedical Engineer",
                    "review_comments": tech_comments,
                    "override_reason": override_reason if is_override else None
                }
                status, res = post_json("review", payload)
                if status == 200:
                    st.success(f"✅ Maintenance decision successfully recorded! Work order set to **{decision}**.")
                    st.info("Recorded in permanent audit log. Notification dispatched to departmental charge nurse.")
                else:
                    st.error(f"Error recording decision: {res.get('detail')}")

else: # Hospital Administrator / Operations Manager
    st.info("""
    **Hospital Administrator Mode**: Executive governance sign-off. Review triage decisions, approve expedited emergency freight for parts, and monitor compliance.
    """)
    with st.form("admin_review_form"):
        st.markdown("#### Executive Governance Review")
        admin_action = st.radio("Executive Action:", ["Approve Current Triage Priority", "Authorize Emergency Escalation", "Reallocate Cross-Facility Backup"])
        admin_notes = st.text_area("Administrative Directives & Budgetary Authorization:")
        
        btn_submit = st.form_submit_button("Authorize Administrative Action", type="primary")
        if btn_submit:
            payload = {
                "equipment_id": eq_id,
                "recommendation": priority,
                "human_decision": priority if "Approve" in admin_action else "CRITICAL",
                "reviewer_role": "Hospital Administrator",
                "review_comments": f"Action: {admin_action} | Notes: {admin_notes}",
                "override_reason": admin_action
            }
            status, res = post_json("review", payload)
            if status == 200:
                st.success("✅ Executive directive logged in compliance audit trail.")
            else:
                st.error(f"Error: {res.get('detail')}")
