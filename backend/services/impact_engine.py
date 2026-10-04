from backend.config import settings

def calculate_urgency_score(procedures) -> float:
    if not procedures:
        return 0.0
    
    urgency_map = {"EMERGENCY": 100.0, "URGENT": 70.0, "ROUTINE": 30.0}
    scores = [urgency_map.get(getattr(p, "urgency", "").upper(), 0.0) for p in procedures]
    return max(scores) if scores else 0.0

def calculate_procedures_affected_score(procedures) -> float:
    count = len(procedures) if procedures else 0
    if count == 0:
        return 0.0
    elif count == 1:
        return 30.0
    elif count == 2:
        return 60.0
    elif count >= 3:
        return 100.0
    return 0.0

def calculate_alternative_risk_score(alternative) -> float:
    if not alternative:
        return 50.0  # UNKNOWN default risk
        
    avail = getattr(alternative, "alternative_available", "UNKNOWN")
    if avail == "YES":
        capacity = getattr(alternative, "capacity_available", True)
        if capacity is False:
            # Alternative hardware exists, but capacity is full
            return 60.0
        return 0.0
    elif avail == "NO":
        return 100.0
    else:  # UNKNOWN
        return 50.0

def calculate_repair_time_score(repair) -> float:
    if not repair:
        return 50.0  # UNKNOWN default
        
    hours_raw = getattr(repair, "estimated_repair_hours", None)
    if hours_raw is None or str(hours_raw).strip() == "":
        return 50.0
        
    try:
        hours = float(hours_raw)
    except (ValueError, TypeError):
        return 50.0

    if hours <= 2:
        return 20.0
    elif hours <= 8:
        return 50.0
    elif hours <= 24:
        return 80.0
    else:
        return 100.0

def calculate_service_criticality_score(service_obj) -> float:
    if not service_obj:
        return 50.0
    try:
        return float(getattr(service_obj, "criticality", 50.0))
    except (ValueError, TypeError):
        return 50.0

def get_priority_level(score: float) -> str:
    if score >= settings.threshold_critical:
        return "CRITICAL"
    elif score >= settings.threshold_high:
        return "HIGH"
    elif score >= settings.threshold_medium:
        return "MEDIUM"
    else:
        return "LOW"

def calculate_impact_score(equipment, procedures, alternative, repair, service_obj) -> float:
    if not equipment or getattr(equipment, "status", "") != "DOWN":
        return 0.0
        
    urgency = calculate_urgency_score(procedures)
    proc_affected = calculate_procedures_affected_score(procedures)
    alt_risk = calculate_alternative_risk_score(alternative)
    rep_time = calculate_repair_time_score(repair)
    srv_crit = calculate_service_criticality_score(service_obj)
    
    score = (
        (urgency * settings.weight_urgency) +
        (proc_affected * settings.weight_procedures_affected) +
        (alt_risk * settings.weight_alternative_risk) +
        (rep_time * settings.weight_repair_time) +
        (srv_crit * settings.weight_service_criticality)
    )
    
    return round(score, 2)
