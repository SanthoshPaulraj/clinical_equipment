import pytest
from datetime import datetime, timedelta
from backend.services.freshness_engine import calculate_freshness, generate_machine_warnings
from backend.services.impact_engine import calculate_impact_score, get_priority_level
from backend.config import settings

# Helper mock objects
class MockObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_calculate_freshness_fresh():
    now = datetime.now()
    ts = (now - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
    assert calculate_freshness(ts) == "FRESH"

def test_calculate_freshness_stale():
    now = datetime.now()
    ts = (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
    assert calculate_freshness(ts) == "STALE"

def test_calculate_freshness_very_stale():
    now = datetime.now()
    ts = (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    assert calculate_freshness(ts) == "VERY_STALE"

def test_calculate_freshness_missing():
    assert calculate_freshness(None) == "MISSING"
    assert calculate_freshness("") == "MISSING"

def test_generate_machine_warnings_equipment_missing():
    equipment = None
    warnings = generate_machine_warnings(equipment, [], None, None, {"equipment": "MISSING"})
    codes = [w["code"] for w in warnings]
    assert "ERR_EQUIPMENT_DATA_MISSING" in codes

def test_generate_machine_warnings_alternative_very_stale_severity():
    alt = MockObj(alternative_available="YES", capacity_available=False, last_updated=(datetime.now() - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"))
    warnings = generate_machine_warnings(None, [], alt, None, {"alternative": "VERY_STALE"})
    severity = [w["severity"] for w in warnings if w["code"] == "WARN_ALTERNATIVE_DATA_VERY_STALE"][0]
    assert severity == "HIGH"

def test_impact_score_basic():
    equipment = MockObj(status="DOWN")
    procedures = []
    alternative = MockObj(alternative_available="YES", capacity_available=True)
    repair = MockObj(estimated_repair_hours=2)
    service = MockObj(criticality=80)
    score = calculate_impact_score(equipment, procedures, alternative, repair, service)
    assert score > 0

def test_priority_level_thresholds():
    assert get_priority_level(settings.threshold_critical) == "CRITICAL"
    assert get_priority_level(settings.threshold_high) == "HIGH"
    assert get_priority_level(settings.threshold_medium) == "MEDIUM"
    assert get_priority_level(settings.threshold_medium - 1) == "LOW"
