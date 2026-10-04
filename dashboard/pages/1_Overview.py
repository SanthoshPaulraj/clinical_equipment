import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import inject_custom_styles, render_role_selector, fetch_json

st.set_page_config(page_title="Overview & Fleet KPIs | MediPulse AI", page_icon="📊", layout="wide")
inject_custom_styles()
role, role_meta = render_role_selector()

st.title("📊 Hospital Fleet Overview & Clinical Impact KPIs")
st.markdown(f"**Viewing Perspective:** `{role}` — {role_meta['description']}")

metrics = fetch_json("dashboard/metrics", default={})
equipment_data = fetch_json("equipment", default=[])
df_equip = pd.DataFrame(equipment_data) if equipment_data else pd.DataFrame()

# 1. Executive Top Metrics Row
if metrics:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Equipment Fleet", metrics.get("total_equipment", 0))
    c2.metric("Active Down Outages", metrics.get("equipment_down", 0), delta=f"{metrics.get('critical', 0)} Critical", delta_color="inverse")
    c3.metric("Procedures Affected", metrics.get("procedures_affected", 0))
    c4.metric("Impacted Care Services", metrics.get("services_affected", 0))
    c5.metric("Audit Verified Reviews", metrics.get("human_reviews_completed", 0))

st.markdown("---")

# 2. Priority Distribution Row
st.subheader("🎯 Active Maintenance Priority Distribution")
p_col1, p_col2, p_col3, p_col4 = st.columns(4)

crit = metrics.get('critical', 0)
high = metrics.get('high', 0)
med = metrics.get('medium', 0)
low = metrics.get('low', 0)

with p_col1:
    st.markdown(f"""
    <div style="background-color: #fef2f2; border: 1px solid #fecaca; border-left: 5px solid #ef4444; border-radius: 8px; padding: 1rem;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #991b1b; text-transform: uppercase;">CRITICAL PRIORITY</div>
        <div style="font-size: 2rem; font-weight: 800; color: #ef4444;">{crit}</div>
        <div style="font-size: 0.75rem; color: #b91c1c;">Emergency cases, no alternative</div>
    </div>
    """, unsafe_allow_html=True)

with p_col2:
    st.markdown(f"""
    <div style="background-color: #fff7ed; border: 1px solid #fed7aa; border-left: 5px solid #f97316; border-radius: 8px; padding: 1rem;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #9a3412; text-transform: uppercase;">HIGH PRIORITY</div>
        <div style="font-size: 2rem; font-weight: 800; color: #f97316;">{high}</div>
        <div style="font-size: 0.75rem; color: #c2410c;">Urgent procedures, capacity strained</div>
    </div>
    """, unsafe_allow_html=True)

with p_col3:
    st.markdown(f"""
    <div style="background-color: #fefce8; border: 1px solid #fef08a; border-left: 5px solid #eab308; border-radius: 8px; padding: 1rem;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #854d0e; text-transform: uppercase;">MEDIUM PRIORITY</div>
        <div style="font-size: 2rem; font-weight: 800; color: #ca8a04;">{med}</div>
        <div style="font-size: 0.75rem; color: #a16207;">Routine care, backup available</div>
    </div>
    """, unsafe_allow_html=True)

with p_col4:
    st.markdown(f"""
    <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-left: 5px solid #22c55e; border-radius: 8px; padding: 1rem;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #166534; text-transform: uppercase;">LOW PRIORITY</div>
        <div style="font-size: 2rem; font-weight: 800; color: #22c55e;">{low}</div>
        <div style="font-size: 0.75rem; color: #15803d;">Nominal impact, long delay safe</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 3. Role-Tailored Analytical Visualizations
if not df_equip.empty:
    down_df = df_equip[df_equip["status"] == "DOWN"].copy()
    
    if role == "Biomedical Engineer":
        st.subheader("🔧 Engineering Triage: Fleet Hardware & Vendor Reliability")
        c_left, c_right = st.columns(2)
        with c_left:
            fig_mfg = px.histogram(
                down_df, 
                x="manufacturer", 
                color="equipment_type", 
                title="Active Outages by Manufacturer & Equipment Type",
                barmode="stack",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_mfg.update_layout(xaxis_title="Manufacturer", yaxis_title="Down Machines", template="plotly_white")
            st.plotly_chart(fig_mfg, use_container_width=True)
            
        with c_right:
            fig_scatter = px.scatter(
                down_df, 
                x="downtime_hours", 
                y="equipment_type", 
                color="criticality", 
                size="downtime_hours",
                title="Downtime Duration vs Equipment Modality",
                color_discrete_map={"HIGH": "#ef4444", "MEDIUM": "#f97316", "LOW": "#22c55e"}
            )
            fig_scatter.update_layout(xaxis_title="Elapsed Downtime (Hours)", yaxis_title="Equipment Modality", template="plotly_white")
            st.plotly_chart(fig_scatter, use_container_width=True)

    elif role == "Clinical Staff":
        st.subheader("🩺 Clinical Impact: Departmental Care Disruption")
        c_left, c_right = st.columns(2)
        with c_left:
            fig_service = px.bar(
                down_df, 
                x="service", 
                color="criticality", 
                title="Equipment Outages by Care Service Unit",
                color_discrete_map={"HIGH": "#ef4444", "MEDIUM": "#f97316", "LOW": "#22c55e"}
            )
            fig_service.update_layout(xaxis_title="Care Unit Service ID", yaxis_title="Outage Count", template="plotly_white")
            st.plotly_chart(fig_service, use_container_width=True)
            
        with c_right:
            fig_dept = px.pie(
                down_df, 
                names="department", 
                title="Outage Distribution Across Hospital Wings & Annexes",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_dept, use_container_width=True)

    else: # Hospital Administrator / Operations Manager
        st.subheader("📊 Executive Operations: SLA Oversight & Capacity Risk")
        c_left, c_right = st.columns(2)
        with c_left:
            status_counts = df_equip["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            fig_fleet = px.pie(
                status_counts, 
                values="Count", 
                names="Status", 
                title="Overall Hospital Fleet Operational Availability",
                hole=0.45,
                color="Status",
                color_discrete_map={"AVAILABLE": "#22c55e", "DOWN": "#ef4444", "MAINTENANCE": "#eab308"}
            )
            st.plotly_chart(fig_fleet, use_container_width=True)
            
        with c_right:
            priority_df = pd.DataFrame({
                "Priority": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                "Count": [crit, high, med, low]
            })
            fig_prio = px.bar(
                priority_df, 
                x="Priority", 
                y="Count", 
                color="Priority",
                title="Prioritization Triage Breakdown",
                color_discrete_map={"CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#eab308", "LOW": "#22c55e"}
            )
            fig_prio.update_layout(template="plotly_white")
            st.plotly_chart(fig_prio, use_container_width=True)
