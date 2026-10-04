from typing import Tuple, List, Dict, Any, Optional

def determine_confidence_and_fallback(freshness: Dict[str, str], alternative, repair) -> Tuple[str, bool, List[str], List[str]]:
    """
    Evaluates operational data integrity and triggers fallback protocols when
    data is missing, very stale, or unconfirmed.
    Returns: (confidence, fallback_triggered, missing_data_warnings, stale_data_warnings)
    """
    confidence = "HIGH"
    fallback_triggered = False
    missing_data_warnings = []
    stale_data_warnings = []
    
    # 1. Check freshness across all operational feeds
    for stream, status in freshness.items():
        stream_name = stream.capitalize()
        if status == "VERY_STALE":
            confidence = "LOW"
            fallback_triggered = True
            stale_data_warnings.append(f"{stream_name} data is VERY STALE (>6 hours old). Schedule may be invalidated.")
        elif status == "STALE":
            if confidence != "LOW":
                confidence = "MEDIUM"
            stale_data_warnings.append(f"{stream_name} data is STALE (>1 hour old). Needs refresh.")
        elif status == "MISSING":
            confidence = "LOW"
            fallback_triggered = True
            missing_data_warnings.append(f"{stream_name} data feed is MISSING.")

    # 2. Check alternative availability state
    if not alternative:
        confidence = "LOW"
        fallback_triggered = True
        missing_data_warnings.append("Alternative equipment record is completely MISSING.")
    else:
        avail = getattr(alternative, "alternative_available", "UNKNOWN")
        if avail == "UNKNOWN":
            confidence = "LOW"
            fallback_triggered = True
            missing_data_warnings.append("Alternative equipment availability is UNKNOWN.")

    # 3. Check repair estimate completeness
    if not repair:
        confidence = "LOW"
        fallback_triggered = True
        missing_data_warnings.append("Repair record is completely MISSING.")
    else:
        hours_raw = getattr(repair, "estimated_repair_hours", None)
        if hours_raw is None or str(hours_raw).strip() == "":
            confidence = "LOW"
            fallback_triggered = True
            missing_data_warnings.append("Estimated repair duration is MISSING.")

    return confidence, fallback_triggered, missing_data_warnings, stale_data_warnings
