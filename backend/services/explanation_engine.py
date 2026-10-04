def generate_explanation(equipment, procedures, alternative, repair, service_obj, missing_data_warnings, stale_data_warnings, fallback_triggered) -> dict:
    factors_increasing = []
    factors_decreasing = []
    
    if not equipment or getattr(equipment, "status", "") != "DOWN":
        factors_decreasing.append("Equipment status is not DOWN; operational impact is nominal.")
        return {
            "factors_increasing": factors_increasing,
            "factors_decreasing": factors_decreasing,
            "missing_data_warnings": missing_data_warnings,
            "stale_data_warnings": stale_data_warnings,
            "fallback_triggered": fallback_triggered
        }
    
    # 1. Procedures & Urgency
    if procedures:
        urgencies = [getattr(p, "urgency", "").upper() for p in procedures]
        if "EMERGENCY" in urgencies:
            factors_increasing.append("Emergency procedure(s) scheduled on this equipment.")
        elif "URGENT" in urgencies:
            factors_increasing.append("Urgent procedure(s) scheduled on this equipment.")
            
        if len(procedures) >= 3:
            factors_increasing.append(f"Heavy case backlog: {len(procedures)} scheduled procedures affected.")
        elif len(procedures) >= 2:
            factors_increasing.append(f"{len(procedures)} procedures potentially affected.")
        elif len(procedures) == 1:
            factors_increasing.append("1 procedure scheduled and awaiting equipment.")
    else:
        factors_decreasing.append("No active procedures currently scheduled.")

    # 2. Alternatives
    if alternative:
        avail = getattr(alternative, "alternative_available", "UNKNOWN")
        if avail == "NO":
            factors_increasing.append("No alternative equipment available in the hospital facility.")
        elif avail == "YES":
            cap = getattr(alternative, "capacity_available", True)
            if cap is False:
                factors_increasing.append("Alternative hardware identified, but current utilization is at 100% capacity.")
            else:
                factors_decreasing.append("Alternative equipment available with verified operational capacity.")
    else:
        factors_increasing.append("Alternative equipment status is unknown; potential single-point-of-failure.")

    # 3. Repair time
    if repair:
        val = getattr(repair, "estimated_repair_hours", None)
        if val is not None and str(val).strip() != "":
            try:
                rep_hours = float(val)
                if rep_hours > 24:
                    factors_increasing.append(f"Extended repair duration estimate ({rep_hours:.1f} hours).")
                elif rep_hours > 8:
                    factors_increasing.append(f"Substantial repair time required ({rep_hours:.1f} hours).")
                elif rep_hours <= 2:
                    factors_decreasing.append(f"Short estimated repair window ({rep_hours:.1f} hours) enables rapid turnaround.")
            except (ValueError, TypeError):
                pass

    # 4. Service Criticality
    if service_obj:
        crit = getattr(service_obj, "criticality", 50)
        srv_name = getattr(service_obj, "service_name", "Clinical Service")
        try:
            crit_val = float(crit)
            if crit_val >= 90:
                factors_increasing.append(f"Critical hospital care service affected ({srv_name} - Acuity {crit_val:.0f}/100).")
            elif crit_val <= 50:
                factors_decreasing.append(f"Lower-acuity clinical service affected ({srv_name} - Acuity {crit_val:.0f}/100).")
        except (ValueError, TypeError):
            pass

    return {
        "factors_increasing": factors_increasing,
        "factors_decreasing": factors_decreasing,
        "missing_data_warnings": missing_data_warnings,
        "stale_data_warnings": stale_data_warnings,
        "fallback_triggered": fallback_triggered
    }
