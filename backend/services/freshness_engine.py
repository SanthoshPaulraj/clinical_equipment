from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.config import settings

def calculate_freshness(last_updated_str: Optional[str]) -> str:
    if not last_updated_str or str(last_updated_str).strip() == "":
        return "MISSING"
        
    try:
        last_updated = datetime.strptime(str(last_updated_str).strip(), "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        diff_hours = (now - last_updated).total_seconds() / 3600.0
        
        if diff_hours < 0:
            # Future timestamp safeguard
            return "FRESH"
        elif diff_hours < settings.fresh_threshold:
            return "FRESH"
        elif diff_hours < settings.stale_threshold:
            return "STALE"
        else:
            return "VERY_STALE"
    except (ValueError, TypeError):
        return "MISSING"

def evaluate_data_freshness(equipment, procedures, alternative, repair) -> Dict[str, str]:
    """
    Evaluates data freshness across all equipment operational streams.
    Hierarchical resolution: MISSING > VERY_STALE > STALE > FRESH.
    """
    freshness = {
        "equipment": calculate_freshness(equipment.last_updated if equipment else None),
        "procedures": "FRESH"
    }
    
    if procedures:
        proc_freshness = [calculate_freshness(p.last_updated) for p in procedures]
        # Strict hierarchical resolution: preserve VERY_STALE and MISSING explicitly!
        if "MISSING" in proc_freshness:
            freshness["procedures"] = "MISSING"
        elif "VERY_STALE" in proc_freshness:
            freshness["procedures"] = "VERY_STALE"
        elif "STALE" in proc_freshness:
            freshness["procedures"] = "STALE"
        else:
            freshness["procedures"] = "FRESH"
    elif equipment and equipment.status == "DOWN":
        # If equipment is down and has no procedure records at all, check if schedule is missing
        freshness["procedures"] = "FRESH"
            
    freshness["alternative"] = calculate_freshness(alternative.last_updated if alternative else None)
    freshness["repair"] = calculate_freshness(repair.last_updated if repair else None)
    
    return freshness

def generate_machine_warnings(equipment, procedures, alternative, repair, freshness: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Generates structured, machine-consumable warnings with actionable remediation protocols.
    """
    warnings = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Equipment freshness warnings
    eq_status = freshness.get("equipment", "MISSING")
    if eq_status == "MISSING":
        warnings.append({
            "code": "ERR_EQUIPMENT_DATA_MISSING",
            "field": "equipment",
            "status": "MISSING",
            "severity": "CRITICAL",
            "message": "Equipment telemetry timestamp is missing.",
            "action_required": "Verify device network connectivity and CMMS telemetry gateway.",
            "timestamp": now_str
        })
    elif eq_status == "VERY_STALE":
        warnings.append({
            "code": "WARN_EQUIPMENT_DATA_VERY_STALE",
            "field": "equipment",
            "status": "VERY_STALE",
            "severity": "HIGH",
            "message": f"Equipment telemetry has not updated in >{settings.stale_threshold} hours.",
            "action_required": "Perform physical or manual CMMS status check before scheduling.",
            "timestamp": now_str
        })
    elif eq_status == "STALE":
        warnings.append({
            "code": "WARN_EQUIPMENT_DATA_STALE",
            "field": "equipment",
            "status": "STALE",
            "severity": "MEDIUM",
            "message": "Equipment status update is older than 1 hour.",
            "action_required": "Poll equipment interface for latest status.",
            "timestamp": now_str
        })

    # 2. Procedure schedule warnings
    proc_status = freshness.get("procedures", "FRESH")
    if proc_status == "MISSING":
        warnings.append({
            "code": "ERR_PROCEDURE_SCHEDULE_MISSING",
            "field": "procedures",
            "status": "MISSING",
            "severity": "HIGH",
            "message": "Scheduled procedure timestamps are missing or corrupted.",
            "action_required": "Query hospital EHR/OR scheduling interface directly.",
            "timestamp": now_str
        })
    elif proc_status == "VERY_STALE":
        warnings.append({
            "code": "WARN_PROCEDURE_SCHEDULE_VERY_STALE",
            "field": "procedures",
            "status": "VERY_STALE",
            "severity": "HIGH",
            "message": f"Procedure schedule has not refreshed in >{settings.stale_threshold} hours. Case list may be inaccurate.",
            "action_required": "Contact departmental charge nurse to confirm scheduled procedures.",
            "timestamp": now_str
        })
    elif proc_status == "STALE":
        warnings.append({
            "code": "WARN_PROCEDURE_SCHEDULE_STALE",
            "field": "procedures",
            "status": "STALE",
            "severity": "MEDIUM",
            "message": "Procedure schedule has not updated in >1 hour.",
            "action_required": "Sync EHR procedure queue to verify scheduled patients.",
            "timestamp": now_str
        })

    # 3. Alternative availability warnings
    alt_status = freshness.get("alternative", "MISSING")
    if not alternative or getattr(alternative, "alternative_available", None) == "UNKNOWN":
        warnings.append({
            "code": "ERR_ALTERNATIVE_AVAILABILITY_UNKNOWN",
            "field": "alternative",
            "status": "MISSING",
            "severity": "HIGH",
            "message": "Alternative equipment backup availability is unconfirmed (UNKNOWN).",
            "action_required": "Contact biomedical fleet coordinator to physically verify backup device.",
            "timestamp": now_str
        })
    elif alt_status == "VERY_STALE":
        warnings.append({
            "code": "WARN_ALTERNATIVE_DATA_VERY_STALE",
            "field": "alternative",
            "status": "VERY_STALE",
            "severity": "HIGH",
            "message": "Alternative equipment availability status is very stale (>6h old).",
            "action_required": "Confirm backup equipment location and power-on readiness.",
            "timestamp": now_str
        })
    elif alt_status == "STALE":
        warnings.append({
            "code": "WARN_ALTERNATIVE_DATA_STALE",
            "field": "alternative",
            "status": "STALE",
            "severity": "LOW",
            "message": "Alternative equipment availability status has not been verified within 1 hour.",
            "action_required": "Perform routine backup check.",
            "timestamp": now_str
        })

    # 4. Repair estimate warnings
    repair_hours = getattr(repair, "estimated_repair_hours", None) if repair else None
    if not repair or repair_hours is None or str(repair_hours).strip() == "":
        warnings.append({
            "code": "ERR_REPAIR_ESTIMATE_MISSING",
            "field": "repair",
            "status": "MISSING",
            "severity": "HIGH",
            "message": "Estimated repair hours are missing from maintenance work order.",
            "action_required": "BMET technician must input diagnostic estimate in CMMS.",
            "timestamp": now_str
        })
    else:
        rep_status = freshness.get("repair", "MISSING")
        if rep_status == "VERY_STALE":
            warnings.append({
                "code": "WARN_REPAIR_DATA_VERY_STALE",
                "field": "repair",
                "status": "VERY_STALE",
                "severity": "MEDIUM",
                "message": "Repair work order update is very stale (>6h old).",
                "action_required": "Request service technician dispatch update.",
                "timestamp": now_str
            })
        elif rep_status == "STALE":
            warnings.append({
                "code": "WARN_REPAIR_DATA_STALE",
                "field": "repair",
                "status": "STALE",
                "severity": "LOW",
                "message": "Repair work order has not updated in >1 hour.",
                "action_required": "Review technician notes.",
                "timestamp": now_str
            })

    return warnings
