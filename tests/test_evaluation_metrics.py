import pytest
import pandas as pd
from scripts.run_evaluation import calculate_independent_ground_truth, run_evaluation
from backend.services.impact_engine import calculate_impact_score

class DummyObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_independent_ground_truth_calculation():
    # Emergency ICU case with no alternative and long duration
    eq_icu = DummyObj(equipment_id="EQ-TEST-1", service="SRV-ICU", status="DOWN", downtime_hours=2.0)
    p_long = DummyObj(duration_minutes=180, urgency="EMERGENCY")
    alt_no = DummyObj(alternative_available="NO")
    srv_icu = DummyObj(service_id="SRV-ICU", criticality=100)
    
    gt_high = calculate_independent_ground_truth(eq_icu, [p_long], alt_no, srv_icu)
    # Acuity=100, Duration=100, Strain=100 -> 0.4*100 + 0.35*100 + 0.25*100 = 100.0
    assert gt_high == 100.0
    
    # Routine Outpatient case with alternative available and short duration
    eq_out = DummyObj(equipment_id="EQ-TEST-2", service="SRV-OUT", status="DOWN", downtime_hours=48.0)
    p_short = DummyObj(duration_minutes=30, urgency="ROUTINE")
    alt_yes = DummyObj(alternative_available="YES", capacity_available=True)
    srv_out = DummyObj(service_id="SRV-OUT", criticality=40)
    
    gt_low = calculate_independent_ground_truth(eq_out, [p_short], alt_yes, srv_out)
    # Acuity=35, Duration=(30/180)*100=16.67, Strain=20 -> 0.4*35 + 0.35*16.67 + 0.25*20 = 14 + 5.83 + 5 = 24.83
    assert gt_low < 35.0
    assert gt_high > gt_low

def test_run_evaluation_metrics_contract():
    results = run_evaluation()
    
    assert "total_scenarios" in results
    assert results["total_scenarios"] > 0
    assert "proposed_pearson" in results
    assert "baseline_pearson" in results
    assert "proposed_precision" in results
    assert "proposed_crit_recall" in results
    
    # Empirical validation: Proposed MUST outperform baseline significantly
    assert results["proposed_pearson"] > 0.70
    assert results["proposed_pearson"] > results["baseline_pearson"] + 0.50
    assert results["proposed_precision"] > results["baseline_precision"]
    assert results["proposed_crit_recall"] > results["baseline_crit_recall"]
    assert results["proposed_precision"] >= 90.0  # Zero or near-zero false highs
