import pytest
from backend.services.fallback_engine import determine_confidence_and_fallback

class DummyObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_fallback_engine_high_confidence():
    freshness = {
        "equipment": "FRESH",
        "procedures": "FRESH",
        "alternative": "FRESH",
        "repair": "FRESH"
    }
    alt = DummyObj(alternative_available="YES")
    rep = DummyObj(estimated_repair_hours=4.0)
    
    conf, fallback, missing_warns, stale_warns = determine_confidence_and_fallback(freshness, alt, rep)
    assert conf == "HIGH"
    assert fallback is False
    assert len(missing_warns) == 0
    assert len(stale_warns) == 0

def test_fallback_engine_stale_degradation():
    freshness = {
        "equipment": "FRESH",
        "procedures": "STALE",
        "alternative": "FRESH",
        "repair": "FRESH"
    }
    alt = DummyObj(alternative_available="YES")
    rep = DummyObj(estimated_repair_hours=4.0)
    
    conf, fallback, missing_warns, stale_warns = determine_confidence_and_fallback(freshness, alt, rep)
    assert conf == "MEDIUM"
    assert fallback is False
    assert len(stale_warns) == 1

def test_fallback_engine_very_stale_triggers_fallback():
    freshness = {
        "equipment": "FRESH",
        "procedures": "VERY_STALE",
        "alternative": "FRESH",
        "repair": "FRESH"
    }
    alt = DummyObj(alternative_available="YES")
    rep = DummyObj(estimated_repair_hours=4.0)
    
    conf, fallback, missing_warns, stale_warns = determine_confidence_and_fallback(freshness, alt, rep)
    assert conf == "LOW"
    assert fallback is True
    assert len(stale_warns) == 1
    assert "VERY STALE" in stale_warns[0]

def test_fallback_engine_missing_data_triggers_fallback():
    # 1. Missing stream in freshness
    freshness = {
        "equipment": "FRESH",
        "procedures": "MISSING",
        "alternative": "FRESH",
        "repair": "FRESH"
    }
    alt = DummyObj(alternative_available="YES")
    rep = DummyObj(estimated_repair_hours=4.0)
    
    conf, fallback, missing_warns, _ = determine_confidence_and_fallback(freshness, alt, rep)
    assert conf == "LOW"
    assert fallback is True
    assert len(missing_warns) > 0

    # 2. Alternative UNKNOWN
    freshness_clean = {k: "FRESH" for k in freshness}
    alt_unk = DummyObj(alternative_available="UNKNOWN")
    conf, fallback, missing_warns, _ = determine_confidence_and_fallback(freshness_clean, alt_unk, rep)
    assert conf == "LOW"
    assert fallback is True
    assert any("UNKNOWN" in w for w in missing_warns)

    # 3. Repair estimate missing
    rep_missing = DummyObj(estimated_repair_hours=None)
    conf, fallback, missing_warns, _ = determine_confidence_and_fallback(freshness_clean, alt, rep_missing)
    assert conf == "LOW"
    assert fallback is True
    assert any("repair" in w.lower() for w in missing_warns)
