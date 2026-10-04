import pytest
from backend.services.impact_engine import (
    calculate_urgency_score, 
    calculate_alternative_risk_score, 
    calculate_procedures_affected_score,
    calculate_repair_time_score,
    calculate_service_criticality_score,
    get_priority_level,
    calculate_impact_score
)
from backend.config import settings

class DummyObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_urgency_scoring():
    # Emergency procedure present -> 100.0
    p1 = DummyObj(urgency="EMERGENCY")
    p2 = DummyObj(urgency="ROUTINE")
    assert calculate_urgency_score([p1, p2]) == 100.0
    
    # Urgent procedure present -> 70.0
    p3 = DummyObj(urgency="URGENT")
    assert calculate_urgency_score([p2, p3]) == 70.0
    
    # Only routine -> 30.0
    assert calculate_urgency_score([p2]) == 30.0
    
    # No procedures -> 0.0
    assert calculate_urgency_score([]) == 0.0

def test_alternative_risk_scoring():
    # No alternative -> 100.0 risk
    alt_no = DummyObj(alternative_available="NO")
    assert calculate_alternative_risk_score(alt_no) == 100.0
    
    # Alternative available with capacity -> 0.0 risk
    alt_yes = DummyObj(alternative_available="YES", capacity_available=True)
    assert calculate_alternative_risk_score(alt_yes) == 0.0
    
    # Alternative available but capacity is full -> 60.0 risk
    alt_capped = DummyObj(alternative_available="YES", capacity_available=False)
    assert calculate_alternative_risk_score(alt_capped) == 60.0
    
    # Unknown alternative -> 50.0 risk
    alt_unk = DummyObj(alternative_available="UNKNOWN")
    assert calculate_alternative_risk_score(alt_unk) == 50.0
    assert calculate_alternative_risk_score(None) == 50.0

def test_repair_time_scoring_and_string_safety():
    """
    Validates repair time scoring and verifies that string repair hours
    do NOT raise TypeError.
    """
    # Numeric values
    assert calculate_repair_time_score(DummyObj(estimated_repair_hours=1.5)) == 20.0
    assert calculate_repair_time_score(DummyObj(estimated_repair_hours=6.0)) == 50.0
    assert calculate_repair_time_score(DummyObj(estimated_repair_hours=16.0)) == 80.0
    assert calculate_repair_time_score(DummyObj(estimated_repair_hours=36.0)) == 100.0
    
    # String representations (critical bug fix test)
    assert calculate_repair_time_score(DummyObj(estimated_repair_hours="1.5")) == 20.0
    assert calculate_repair_time_score(DummyObj(estimated_repair_hours="10.4")) == 80.0
    assert calculate_repair_time_score(DummyObj(estimated_repair_hours="")) == 50.0
    assert calculate_repair_time_score(DummyObj(estimated_repair_hours=None)) == 50.0
    assert calculate_repair_time_score(None) == 50.0

def test_service_criticality_scoring():
    srv_icu = DummyObj(criticality=100)
    assert calculate_service_criticality_score(srv_icu) == 100.0
    
    srv_str = DummyObj(criticality="90")
    assert calculate_service_criticality_score(srv_str) == 90.0
    
    assert calculate_service_criticality_score(None) == 50.0

def test_priority_threshold_mapping():
    assert get_priority_level(95.0) == "CRITICAL"
    assert get_priority_level(90.0) == "CRITICAL"
    assert get_priority_level(85.0) == "HIGH"
    assert get_priority_level(75.0) == "HIGH"
    assert get_priority_level(60.0) == "MEDIUM"
    assert get_priority_level(50.0) == "MEDIUM"
    assert get_priority_level(40.0) == "LOW"

def test_calculate_impact_score_integration():
    eq_down = DummyObj(status="DOWN")
    p1 = DummyObj(urgency="EMERGENCY")
    p2 = DummyObj(urgency="URGENT")
    p3 = DummyObj(urgency="ROUTINE")
    alt = DummyObj(alternative_available="NO")
    rep = DummyObj(estimated_repair_hours=30.0)
    srv = DummyObj(criticality=100)
    
    score = calculate_impact_score(eq_down, [p1, p2, p3], alt, rep, srv)
    assert score >= 90.0
    assert get_priority_level(score) == "CRITICAL"
    
    # When equipment is not DOWN, score must be 0.0
    eq_avail = DummyObj(status="AVAILABLE")
    assert calculate_impact_score(eq_avail, [p1], alt, rep, srv) == 0.0
