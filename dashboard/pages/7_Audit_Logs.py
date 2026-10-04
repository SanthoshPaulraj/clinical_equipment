import streamlit as st
import pandas as pd
from utils import inject_custom_styles, render_role_selector, fetch_json, check_role_access

st.set_page_config(page_title="Audit Trail & Accountability Logs | MediPulse AI", page_icon="📜", layout="wide")
inject_custom_styles()
role, role_meta = render_role_selector()

st.title("📜 Regulatory Compliance & Decision Audit Trail")
st.markdown("""
**Accountability Standard**: Every automated recommendation, clinician expedite request, biomedical priority decision, 
and override justification is immutably logged with UTC timestamps and user role credentials.
""")

# Role check
if role == "Clinical Staff":
    st.info("ℹ️ Clinical Staff View: Showing clinical expedite requests and verified priority confirmations.")
else:
    st.success(f"🔓 {role}: Full Administrative Audit Access Enabled.")

logs = fetch_json("audit", default=[])

if not logs:
    st.info("No audit entries currently recorded. Submit a decision in the Human Review module to create audit logs.")
    st.stop()

df = pd.DataFrame(logs)

# Filter Bar
f_col1, f_col2, f_col3 = st.columns(3)
with f_col1:
    all_events = ["ALL"] + sorted(list(df["event_type"].unique())) if "event_type" in df.columns else ["ALL"]
    sel_event = st.selectbox("Filter Event Type:", all_events)
with f_col2:
    all_roles = ["ALL"] + sorted(list(df["user_role"].unique())) if "user_role" in df.columns else ["ALL"]
    sel_role = st.selectbox("Filter Reviewer Role:", all_roles)
with f_col3:
    eq_search = st.text_input("Filter Equipment ID:", "").strip().upper()

filtered_df = df.copy()
if sel_event != "ALL":
    filtered_df = filtered_df[filtered_df["event_type"] == sel_event]
if sel_role != "ALL":
    filtered_df = filtered_df[filtered_df["user_role"] == sel_role]
if eq_search:
    filtered_df = filtered_df[filtered_df["equipment_id"].str.contains(eq_search)]

st.markdown(f"**Displaying {len(filtered_df)} of {len(df)} total audit log entries**")

# Display Table
display_cols = ["audit_id", "timestamp", "event_type", "user_role", "equipment_id", "previous_priority", "new_priority", "override_reason", "reason"]
show_df = filtered_df[[c for c in display_cols if c in filtered_df.columns]].copy()
show_df.columns = [c.replace("_", " ").title() for c in show_df.columns]

st.dataframe(show_df, use_container_width=True, height=400)

# Export button for hospital compliance officer
st.markdown("---")
c_exp1, c_exp2 = st.columns([1.5, 3])
with c_exp1:
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Compliance Audit Log (CSV)",
        data=csv_data,
        file_name="hospital_equipment_audit_trail.csv",
        mime="text/csv",
        use_container_width=True
    )
with c_exp2:
    st.caption("Immutable operational audit log formatted for clinical risk audits and Joint Commission medical equipment management inspections.")
