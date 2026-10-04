from datetime import datetime, timedelta
import pytest
from backend.services.freshness_engine import calculate_freshness, evaluate_data_freshness, generate_machine_warnings
from backend.config import settings

class DummyObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_calculate_freshness_states():
    now = datetime.now()
    
    # Missing / None / Empty
    assert calculate_freshness(None) == "MISSING"
    assert calculate_freshness("") == "MISSING"
    assert calculate_freshness("invalid-date") == "MISSING"
    
    # Fresh (< 1 hour)
    fresh_time = (now - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
    assert calculate_freshness(fresh_time) == "FRESH"
    
    # Stale (1 - 6 hours)
    stale_time = (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
    assert calculate_freshness(stale_time) == "STALE"
    
    # Very Stale (> 6 hours)
    very_stale_time = (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    assert calculate_freshness(very_stale_time) == "VERY_STALE"

def test_procedure_freshness_hierarchical_resolution():
    """
    Validates the fix for procedure freshness logic:
    VERY_STALE and MISSING must NOT be downgraded to STALE!
    """
    now = datetime.now()
    fresh_time = (now - timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
    stale_time = (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    very_stale_time = (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    
    eq = DummyObj(last_updated=fresh_time, status="DOWN")
    alt = DummyObj(last_updated=fresh_time, alternative_available="YES")
    rep = DummyObj(last_updated=fresh_time, estimated_repair_hours=5.0)
    
    # 1. All fresh procedures
    p1 = DummyObj(last_updated=fresh_time)
    p2 = DummyObj(last_updated=fresh_time)
    res_fresh = evaluate_data_freshness(eq, [p1, p2], alt, rep)
    assert res_fresh["procedures"] == "FRESH"
    
    # 2. Contains STALE procedure -> STALE
    p_stale = DummyObj(last_updated=stale_time)
    res_stale = evaluate_data_freshness(eq, [p1, p_stale], alt, rep)
    assert res_stale["procedures"] == "STALE"
    
    # 3. Contains VERY_STALE procedure -> must be VERY_STALE, NOT STALE!
    p_very_stale = DummyObj(last_updated=very_stale_time)
    res_very_stale = evaluate_data_freshness(eq, [p1, p_stale, p_very_stale], alt, rep)
    assert res_very_stale["procedures"] == "VERY_STALE"
    
    # 4. Contains MISSING procedure timestamp -> must be MISSING
    p_missing = DummyObj(last_updated=None)
    res_missing = evaluate_data_freshness(eq, [p1, p_very_stale, p_missing], alt, rep)
    assert res_missing["procedures"] == "MISSING"

def test_generate_machine_warnings_structured_format():
    now = datetime.now()
    very_stale_time = (now - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M:%S")
    
    eq = DummyObj(last_updated=very_stale_time, status="DOWN")
    alt = DummyObj(last_updated=very_stale_time, alternative_available="UNKNOWN")
    rep = DummyObj(last_updated=None, estimated_repair_hours=None)
    p = DummyObj(last_updated=very_stale_time)
    
    freshness = evaluate_data_freshness(eq, [p], alt, rep)
    warnings = generate_machine_warnings(eq, [p], alt, rep, freshness)
    
    assert isinstance(warnings, list)
    assert len(warnings) > 0
    
    # Verify machine-consumable keys
    for w in warnings:
        assert "code" in w
        assert "field" in w
        assert "status" in w
        assert "severity" in w
        assert "message" in w
        assert "action_required" in w
        assert w["severity"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        
    codes = [w["code"] for w in warnings]
    assert "ERR_ALTERNATIVE_AVAILABILITY_UNKNOWN" in codes
    assert "ERR_REPAIR_ESTIMATE_MISSING" in codes
    assert "WARN_PROCEDURE_SCHEDULE_VERY_STALE" in codes
