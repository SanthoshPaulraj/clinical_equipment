import streamlit as st
import pandas as pd
import plotly.express as px
from utils import inject_custom_styles, render_role_selector, fetch_json

st.set_page_config(page_title="Prioritization Queue | MediPulse AI", page_icon="🗂️", layout="wide")
inject_custom_styles()
role, role_meta = render_role_selector()

st.title("🗂️ Clinical-Impact Equipment Maintenance Queue")
st.markdown(f"**Active Operational Mode:** `{role}` — Prioritizing work orders by avoided clinical disruption.")

# Fast batch fetch
with st.spinner("Fetching real-time equipment triage assessments..."):
    summary_data = fetch_json("impact-summary?status=DOWN", default=[])

if not summary_data:
    st.error("No active DOWN equipment found or could not connect to backend API. Please ensure the backend is running.")
    st.stop()

df = pd.DataFrame(summary_data)

# Interactive Filter Controls Bar
st.markdown("### 🔍 Filter & Search Queue")
f_col1, f_col2, f_col3, f_col4 = st.columns(4)

with f_col1:
    search_query = st.text_input("Search ID, Type, or Manufacturer:", "").strip().lower()
with f_col2:
    all_prios = ["ALL"] + sorted(list(df["priority"].unique()))
    selected_prio = st.selectbox("Priority Level", all_prios, index=0)
with f_col3:
    all_depts = ["ALL"] + sorted(list(df["department"].unique()))
    selected_dept = st.selectbox("Hospital Wing / Department", all_depts, index=0)
with f_col4:
    all_conf = ["ALL"] + sorted(list(df["confidence"].unique()))
    selected_conf = st.selectbox("Data Confidence", all_conf, index=0)

# Filter logic
filtered_df = df.copy()
if search_query:
    filtered_df = filtered_df[
        filtered_df["equipment_id"].str.lower().str.contains(search_query) |
        filtered_df["equipment_type"].str.lower().str.contains(search_query) |
        filtered_df["manufacturer"].str.lower().str.contains(search_query)
    ]
if selected_prio != "ALL":
    filtered_df = filtered_df[filtered_df["priority"] == selected_prio]
if selected_dept != "ALL":
    filtered_df = filtered_df[filtered_df["department"] == selected_dept]
if selected_conf != "ALL":
    filtered_df = filtered_df[filtered_df["confidence"] == selected_conf]

st.markdown(f"**Showing {len(filtered_df)} of {len(df)} active outage work orders**")

# Priority Matrix Visualization: Clinical Impact vs Elapsed Downtime
st.markdown("---")
st.subheader("🎯 Triage Decision Matrix: Clinical Impact Score vs. Elapsed Downtime Hours")
st.markdown("""
*Notice the upper-left quadrant (**High Clinical Impact, Low Downtime**): These are critical medical emergencies that legacy downtime sorting ignored because they happened recently, but the Clinical Impact Engine immediately elevates.*
""")

fig_matrix = px.scatter(
    df,
    x="downtime_hours",
    y="score",
    color="priority",
    size="score",
    hover_name="equipment_id",
    hover_data=["equipment_type", "department", "service", "confidence"],
    color_discrete_map={"CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#eab308", "LOW": "#22c55e"},
    title="Clinical Impact Score vs Elapsed Downtime (Hours)"
)
# Add quadrant guide lines
fig_matrix.add_hline(y=75, line_dash="dash", line_color="#94a3b8", annotation_text="High Clinical Impact Threshold (Score >= 75)")
fig_matrix.add_vline(x=24, line_dash="dash", line_color="#94a3b8", annotation_text="24h Downtime Threshold")
fig_matrix.update_layout(xaxis_title="Elapsed Downtime Duration (Hours)", yaxis_title="Clinical Impact Score (0 - 100)", template="plotly_white")
st.plotly_chart(fig_matrix, use_container_width=True)

st.markdown("---")

# Data Table Display with Formatted Columns
st.subheader("📋 Ranked Maintenance Triage Table")

display_cols = [
    "equipment_id", "equipment_type", "department", "service", "downtime_hours",
    "score", "priority", "confidence", "fallback_triggered", "warnings_count"
]
table_df = filtered_df[display_cols].copy()
table_df.columns = [
    "Equipment ID", "Type", "Location", "Service", "Downtime (h)",
    "Impact Score", "Priority", "Confidence", "Fallback Active", "Warnings"
]

st.dataframe(
    table_df.style.background_gradient(subset=["Impact Score"], cmap="Reds"),
    use_container_width=True,
    height=380
)

# Role-tailored action & drill-down selection
st.markdown("---")
st.subheader("🔍 Select Work Order for Verification & Review")

selected_eq_id = st.selectbox(
    "Choose Equipment ID to drill down:",
    filtered_df["equipment_id"].tolist() if not filtered_df.empty else []
)

c_act1, c_act2, c_act3 = st.columns([1.5, 1.5, 3])
with c_act1:
    if st.button("🚀 Proceed to Human Review", type="primary", use_container_width=True):
        if selected_eq_id:
            st.session_state["review_equipment_id"] = selected_eq_id
            st.switch_page("pages/3_Human_Review.py")

with c_act2:
    if role == "Hospital Administrator / Operations Manager":
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Triage Queue (CSV)",
            data=csv_data,
            file_name="clinical_maintenance_queue.csv",
            mime="text/csv",
            use_container_width=True
        )
    elif role == "Clinical Staff":
        st.info("ℹ️ Select a machine to submit a Clinical Urgency Expedite Request.")
    else:
        st.info("ℹ️ Select a machine to inspect telemetry and dispatch BMET technician.")
