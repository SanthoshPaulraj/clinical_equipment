import streamlit as st
import pandas as pd
from utils import inject_custom_styles, render_role_selector, fetch_json

st.set_page_config(page_title="Error Analysis & Edge Cases | MediPulse AI", page_icon="⚠️", layout="wide")
inject_custom_styles()
role, role_meta = render_role_selector()

st.title("⚠️ Error Analysis, Edge Cases & Fallback Protocols")
st.markdown("""
A responsible AI system operating in a hospital must **fail safely**. When operational data is missing, stale, or conflicting, 
the system must never make silent optimistic assumptions. This module tests **three critical edge failure modes** 
and demonstrates automated fallback safeguards and machine-consumable warnings.
""")

tab_cases, tab_simulator = st.tabs([
    "🧪 Three Mandatory Edge & Failure Cases",
    "🎮 Interactive Outage Perturbation Simulator"
])

with tab_cases:
    st.subheader("1. Edge Case 1: Missing Alternative Equipment Availability")
    c1_left, c1_right = st.columns([1, 1.2])
    with c1_left:
        st.markdown("""
        **Operational Vulnerability:**  
        The CMMS record indicates an alternative hardware asset ID, but the availability status is `UNKNOWN` (e.g. device is being sanitized, transported, or in unscheduled maintenance).
        
        **Dangerous Failure Mode in Legacy Systems:**  
        Assuming an alternative is available when it is not risks diverting a surgical patient to an inoperable room.
        
        **System Safeguard:**  
        1. Assigns a conservative default risk score ($50.0 / 100$).
        2. Drops system confidence to **`LOW`**.
        3. Generates structured machine warning: `ERR_ALTERNATIVE_AVAILABILITY_UNKNOWN`.
        4. Triggers mandatory Fallback Human Verification.
        """)
    with c1_right:
        st.markdown("""
        ```json
        {
          "code": "ERR_ALTERNATIVE_AVAILABILITY_UNKNOWN",
          "field": "alternative",
          "status": "MISSING",
          "severity": "HIGH",
          "message": "Alternative equipment backup availability is unconfirmed (UNKNOWN).",
          "action_required": "Contact biomedical fleet coordinator to physically verify backup device.",
          "fallback_triggered": true,
          "confidence": "LOW"
        }
        ```
        """)

    st.markdown("---")

    st.subheader("2. Edge Case 2: Very Stale Procedure Schedules (>6 Hours)")
    c2_left, c2_right = st.columns([1, 1.2])
    with c2_left:
        st.markdown("""
        **Operational Vulnerability:**  
        The hospital EHR/OR scheduling interface experienced a network timeout; scheduled procedure records for the room are $8.5$ hours old.
        
        **Dangerous Failure Mode in Legacy Systems:**  
        A patient scheduled for an emergency procedure 2 hours ago might appear as "no procedures scheduled" if the feed is stale, causing the system to deprioritize the repair.
        
        **System Safeguard:**  
        1. Procedure freshness engine maps status strictly to **`VERY_STALE`** (resolving prior bug where VERY_STALE was downgraded to STALE).
        2. Downgrades data confidence to **`LOW`**.
        3. Issues machine warning: `WARN_PROCEDURE_SCHEDULE_VERY_STALE`.
        4. Displays prominent amber/red status pills on dashboard triage views.
        """)
    with c2_right:
        st.markdown("""
        ```json
        {
          "code": "WARN_PROCEDURE_SCHEDULE_VERY_STALE",
          "field": "procedures",
          "status": "VERY_STALE",
          "severity": "HIGH",
          "message": "Procedure schedule has not refreshed in >6 hours. Case list may be inaccurate.",
          "action_required": "Contact departmental charge nurse to confirm scheduled procedures.",
          "fallback_triggered": true,
          "confidence": "LOW"
        }
        ```
        """)

    st.markdown("---")

    st.subheader("3. Edge Case 3: Missing Repair Duration Estimate")
    c3_left, c3_right = st.columns([1, 1.2])
    with c3_left:
        st.markdown("""
        **Operational Vulnerability:**  
        A technician logged an outage ticket but left the `estimated_repair_hours` field blank while awaiting diagnostic tools.
        
        **Dangerous Failure Mode in Legacy Systems:**  
        String or null values can cause runtime `TypeError` crashes or silently treat repair time as 0 hours.
        
        **System Safeguard:**  
        1. Safe float coercion with try/except prevents unhandled runtime exceptions.
        2. Assigns balanced risk score ($50.0 / 100$).
        3. Issues machine warning: `ERR_REPAIR_ESTIMATE_MISSING`.
        4. Triggers fallback review prompting BMET to input initial diagnostic triage hours.
        """)
    with c3_right:
        st.markdown("""
        ```json
        {
          "code": "ERR_REPAIR_ESTIMATE_MISSING",
          "field": "repair",
          "status": "MISSING",
          "severity": "HIGH",
          "message": "Estimated repair hours are missing from maintenance work order.",
          "action_required": "BMET technician must input diagnostic estimate in CMMS.",
          "fallback_triggered": true,
          "confidence": "LOW"
        }
        ```
        """)

with tab_simulator:
    st.subheader("🎮 Real-Time Outage Perturbation & Machine Warning Inspector")
    st.markdown("Select an active down equipment from the fleet to inspect its live freshness state and machine warnings:")
    
    down_equipment = fetch_json("equipment", default=[])
    down_ids = [e["equipment_id"] for e in down_equipment if e.get("status") == "DOWN"] if down_equipment else []
    
    if down_ids:
        test_id = st.selectbox("Select Equipment ID to inspect:", down_ids, key="sim_select")
        impact = fetch_json(f"impact/{test_id}")
        
        if impact:
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.markdown(f"#### Status for `{test_id}`")
                st.write(f"**Score:** `{impact.get('score')}`")
                st.write(f"**Priority:** `{impact.get('priority')}`")
                st.write(f"**Confidence:** `{impact.get('confidence')}`")
                
                st.markdown("##### Freshness Mapping:")
                st.json(impact.get("freshness", {}))
                
            with col_res2:
                st.markdown("#### Machine-Consumable Warnings:")
                warnings = impact.get("machine_warnings", [])
                if warnings:
                    for w in warnings:
                        st.error(f"[{w.get('code')}] {w.get('message')} — Action: {w.get('action_required')}")
                else:
                    st.success("✅ All operational feeds for this work order are FRESH and complete.")
                    
                st.markdown("##### Full Machine-Readable JSON Payload:")
                st.json(warnings)
    else:
        st.info("No down equipment found to simulate.")
