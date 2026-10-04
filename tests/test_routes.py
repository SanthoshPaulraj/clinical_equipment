import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend import models

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_equipment_endpoints():
    # List equipment
    response = client.get("/api/equipment?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5
    if data:
        eq_id = data[0]["equipment_id"]
        # Single equipment by ID
        res_single = client.get(f"/api/equipment/{eq_id}")
        assert res_single.status_code == 200
        assert res_single.json()["equipment_id"] == eq_id

    # 404 test
    res_404 = client.get("/api/equipment/NON-EXISTENT-ID-999")
    assert res_404.status_code == 404

def test_get_procedures_endpoint():
    response = client.get("/api/procedures?limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_impact_endpoint():
    # Fetch first equipment
    eq_res = client.get("/api/equipment?limit=1")
    eq_list = eq_res.json()
    if eq_list:
        eq_id = eq_list[0]["equipment_id"]
        res = client.get(f"/api/impact/{eq_id}")
        assert res.status_code == 200
        impact = res.json()
        assert "score" in impact
        assert "priority" in impact
        assert "confidence" in impact
        assert "explanation" in impact
        assert "freshness" in impact
        assert "machine_warnings" in impact
        assert impact["priority"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        assert impact["confidence"] in ["HIGH", "MEDIUM", "LOW"]

def test_get_impact_summary_batch_endpoint():
    res = client.get("/api/impact-summary?status=DOWN")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    if items:
        first = items[0]
        assert "equipment_id" in first
        assert "score" in first
        assert "priority" in first
        assert "confidence" in first
        assert "fallback_triggered" in first
        assert "warnings_count" in first

def test_get_dashboard_metrics():
    res = client.get("/api/dashboard/metrics")
    assert res.status_code == 200
    metrics = res.json()
    assert "total_equipment" in metrics
    assert "equipment_down" in metrics
    assert "critical" in metrics
    assert "high" in metrics
    assert "medium" in metrics
    assert "low" in metrics
    assert "procedures_affected" in metrics

def test_create_review_workflow():
    eq_res = client.get("/api/equipment?limit=1")
    if not eq_res.json():
        pytest.skip("No equipment available for review test")
    eq_id = eq_res.json()[0]["equipment_id"]

    # 1. Accept recommendation
    payload_accept = {
        "equipment_id": eq_id,
        "recommendation": "HIGH",
        "human_decision": "HIGH",
        "reviewer_role": "Biomedical Engineer",
        "review_comments": "Verified parts and proceeding with service."
    }
    res_accept = client.post("/api/review", json=payload_accept)
    assert res_accept.status_code == 200
    assert res_accept.json()["status"] == "success"

    # 2. Clinical Staff Expedite Request (Valid)
    payload_expedite = {
        "equipment_id": eq_id,
        "recommendation": "MEDIUM",
        "human_decision": "CRITICAL",
        "reviewer_role": "Clinical Staff",
        "review_comments": "Patient condition worsening in ICU.",
        "override_reason": "Clinical Expedite Request: Emergency surgery patient arriving in 15 minutes."
    }
    res_expedite = client.post("/api/review", json=payload_expedite)
    assert res_expedite.status_code == 200
    assert res_expedite.json()["status"] == "success"

    # 3. Clinical Staff unauthorized priority override (WITHOUT expedite reason) -> 403 Forbidden
    payload_unauthorized = {
        "equipment_id": eq_id,
        "recommendation": "HIGH",
        "human_decision": "LOW",
        "reviewer_role": "Clinical Staff",
        "review_comments": "Unsanctioned work order priority downgrade.",
        "override_reason": "Routine nurse preference"
    }
    res_unauth = client.post("/api/review", json=payload_unauthorized)
    assert res_unauth.status_code == 403
    assert "authorized for clinical expedite requests only" in res_unauth.json()["detail"].lower()

    # 4. Override WITHOUT reason -> must return 422 Unprocessable Entity
    payload_invalid = {
        "equipment_id": eq_id,
        "recommendation": "HIGH",
        "human_decision": "LOW",
        "reviewer_role": "Biomedical Engineer",
        "override_reason": ""  # Missing mandatory justification
    }
    res_invalid = client.post("/api/review", json=payload_invalid)
    assert res_invalid.status_code == 422

    # 5. Verify in audit log
    audit_res = client.get(f"/api/audit?equipment_id={eq_id}")
    assert audit_res.status_code == 200
    audit_entries = audit_res.json()
    assert len(audit_entries) >= 2
