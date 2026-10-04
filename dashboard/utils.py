import streamlit as st
import requests
import pandas as pd
from typing import Dict, Any, List, Optional

API_BASE = "http://localhost:8000/api"

ROLES = [
    "Biomedical Engineer",
    "Clinical Staff",
    "Hospital Administrator / Operations Manager"
]

ROLE_PERMISSIONS = {
    "Biomedical Engineer": {
        "badge_color": "#2563EB",
        "icon": "🔧",
        "can_override_priority": True,
        "can_dispatch_repair": True,
        "can_view_audit": True,
        "can_run_evaluation": True,
        "description": "Authorized to triage equipment work orders, verify technical telemetry, and submit maintenance overrides."
    },
    "Clinical Staff": {
        "badge_color": "#059669",
        "icon": "🩺",
        "can_override_priority": False,
        "can_dispatch_repair": False,
        "can_view_audit": False,
        "can_run_evaluation": False,
        "description": "Authorized to view clinical delay risks, track procedure schedules, and submit clinical urgency expedite requests."
    },
    "Hospital Administrator / Operations Manager": {
        "badge_color": "#7C3AED",
        "icon": "📊",
        "can_override_priority": True,
        "can_dispatch_repair": True,
        "can_view_audit": True,
        "can_run_evaluation": True,
        "description": "Executive governance view with full access to audit trails, SLA compliance, cross-department resources, and risk oversight."
    }
}

def inject_custom_styles():
    """
    Injects hospital command-center CSS for a polished, modern, clinical aesthetic.
    """
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .main-header {
            padding: 1.2rem 1.5rem;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border-radius: 12px;
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #3b82f6;
        }
        
        .kpi-card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 1.2rem;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
            transition: transform 0.15s ease-in-out;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .role-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.35rem 0.8rem;
            border-radius: 9999px;
            font-size: 0.825rem;
            font-weight: 600;
            color: white;
            margin-bottom: 1rem;
        }
        
        .badge-critical {
            background-color: #ef4444;
            color: white;
            padding: 0.2rem 0.55rem;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.75rem;
        }
        .badge-high {
            background-color: #f97316;
            color: white;
            padding: 0.2rem 0.55rem;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.75rem;
        }
        .badge-medium {
            background-color: #eab308;
            color: #0f172a;
            padding: 0.2rem 0.55rem;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.75rem;
        }
        .badge-low {
            background-color: #22c55e;
            color: white;
            padding: 0.2rem 0.55rem;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.75rem;
        }
        
        .badge-fresh {
            background-color: #ecfdf5;
            color: #065f46;
            border: 1px solid #a7f3d0;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-stale {
            background-color: #fffbeb;
            color: #92400e;
            border: 1px solid #fde68a;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-very-stale {
            background-color: #fff1f2;
            color: #9f1239;
            border: 1px solid #fecdd3;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
        }
        .badge-missing {
            background-color: #fef2f2;
            color: #b91c1c;
            border: 1px solid #f87171;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
        }
        
        .machine-warning-box {
            background-color: #fef2f2;
            border-left: 4px solid #ef4444;
            padding: 0.8rem 1rem;
            border-radius: 0 8px 8px 0;
            margin-bottom: 0.75rem;
            font-size: 0.875rem;
        }
        
        .fallback-alert {
            background: linear-gradient(90deg, #fff1f2 0%, #fee2e2 100%);
            border: 1px solid #fca5a5;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

def render_role_selector():
    """
    Renders the persistent role switcher in the sidebar and returns current role info.
    """
    if "user_role" not in st.session_state:
        st.session_state["user_role"] = "Biomedical Engineer"
        
    st.sidebar.markdown("### 👤 User Access & Role")
    current_role = st.sidebar.selectbox(
        "Current Session Role",
        ROLES,
        index=ROLES.index(st.session_state["user_role"]),
        key="role_select_box"
    )
    st.session_state["user_role"] = current_role
    role_meta = ROLE_PERMISSIONS[current_role]
    
    st.sidebar.markdown(f"""
    <div style="background-color: {role_meta['badge_color']}; color: white; padding: 0.4rem 0.8rem; border-radius: 8px; font-size: 0.825rem; font-weight: 600; margin-bottom: 0.5rem;">
        {role_meta['icon']} {current_role}
    </div>
    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 1rem;">
        {role_meta['description']}
    </div>
    """, unsafe_allow_html=True)
    
    return current_role, role_meta

def check_role_access(required_permission: str, redirect_message: str = "Access Restricted") -> bool:
    """
    Enforces real access control gating. If user lacks permission, renders a clear warning.
    """
    role = st.session_state.get("user_role", "Biomedical Engineer")
    meta = ROLE_PERMISSIONS.get(role, {})
    if not meta.get(required_permission, False):
        st.error(f"⛔ {redirect_message}")
        st.info(f"Your current role is **{role}**. This action requires higher operational permissions. Switch role in the sidebar if you have elevated credentials.")
        return False
    return True

def fetch_json(endpoint: str, default=None):
    try:
        res = requests.get(f"{API_BASE}/{endpoint.lstrip('/')}", timeout=10)
        if res.status_code == 200:
            return res.json()
        return default
    except Exception as e:
        return default

def post_json(endpoint: str, payload: dict):
    try:
        res = requests.post(f"{API_BASE}/{endpoint.lstrip('/')}", json=payload, timeout=10)
        return res.status_code, res.json()
    except Exception as e:
        return 500, {"detail": str(e)}
