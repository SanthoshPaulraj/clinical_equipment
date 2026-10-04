from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from backend.database import get_db
from backend import models, schemas
from backend.services.impact_engine import calculate_impact_score, get_priority_level
from backend.services.explanation_engine import generate_explanation
from backend.services.freshness_engine import evaluate_data_freshness, generate_machine_warnings
from backend.services.fallback_engine import determine_confidence_and_fallback

router = APIRouter()

@router.get("/impact/{equipment_id}", response_model=schemas.ImpactResponse)
def get_equipment_impact(equipment_id: str, db: Session = Depends(get_db)):
    eq = db.query(models.Equipment).filter(models.Equipment.equipment_id == equipment_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
        
    procedures = db.query(models.Procedure).filter(models.Procedure.required_equipment_id == equipment_id).all()
    alternative = db.query(models.Alternative).filter(models.Alternative.equipment_id == equipment_id).first()
    repair = db.query(models.Repair).filter(models.Repair.equipment_id == equipment_id).first()
    service_obj = db.query(models.Service).filter(models.Service.service_id == eq.service).first()
    
    # 1. Freshness
    freshness = evaluate_data_freshness(eq, procedures, alternative, repair)
    
    # 2. Confidence & Fallback
    confidence, fallback_triggered, missing_warn, stale_warn = determine_confidence_and_fallback(
        freshness, alternative, repair
    )
    
    # 3. Calculate Score & Priority
    score = calculate_impact_score(eq, procedures, alternative, repair, service_obj)
    priority = get_priority_level(score)
    
    # 4. Explanation
    explanation_dict = generate_explanation(
        eq, procedures, alternative, repair, service_obj,
        missing_warn, stale_warn, fallback_triggered
    )
    
    # 5. Machine-consumable warnings
    machine_warnings = generate_machine_warnings(eq, procedures, alternative, repair, freshness)
    
    # 6. Save or update DB record for audit and history
    impact_record = db.query(models.ImpactScore).filter(models.ImpactScore.equipment_id == equipment_id).first()
    if not impact_record:
        impact_record = models.ImpactScore(equipment_id=equipment_id)
        db.add(impact_record)
        
    impact_record.score = score
    impact_record.priority = priority
    impact_record.confidence = confidence
    impact_record.explanation = str(explanation_dict)
    impact_record.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.commit()
    
    return schemas.ImpactResponse(
        equipment_id=equipment_id,
        score=score,
        priority=priority,
        confidence=confidence,
        explanation=schemas.ImpactExplanation(**explanation_dict),
        freshness=freshness,
        machine_warnings=[schemas.MachineWarning(**w) for w in machine_warnings]
    )

@router.get("/impact-summary", response_model=List[schemas.EquipmentImpactSummary])
def get_all_impact_summary(status: Optional[str] = "DOWN", db: Session = Depends(get_db)):
    """
    High-performance batch endpoint: returns all equipment with computed clinical impact scores,
    priorities, confidence states, and machine warning counts in a single query.
    """
    query = db.query(models.Equipment)
    if status and status.upper() != "ALL":
        query = query.filter(models.Equipment.status == status.upper())
    equipment_list = query.all()

    # Pre-fetch lookup tables for efficiency
    all_procedures = db.query(models.Procedure).all()
    proc_map = {}
    for p in all_procedures:
        proc_map.setdefault(p.required_equipment_id, []).append(p)
        
    all_alternatives = {a.equipment_id: a for a in db.query(models.Alternative).all()}
    all_repairs = {r.equipment_id: r for r in db.query(models.Repair).all()}
    all_services = {s.service_id: s for s in db.query(models.Service).all()}

    results = []
    for eq in equipment_list:
        procs = proc_map.get(eq.equipment_id, [])
        alt = all_alternatives.get(eq.equipment_id)
        rep = all_repairs.get(eq.equipment_id)
        srv = all_services.get(eq.service)

        freshness = evaluate_data_freshness(eq, procs, alt, rep)
        confidence, fallback_triggered, _, _ = determine_confidence_and_fallback(freshness, alt, rep)
        score = calculate_impact_score(eq, procs, alt, rep, srv)
        priority = get_priority_level(score)
        machine_warnings = generate_machine_warnings(eq, procs, alt, rep, freshness)

        # Update DB impact record
        impact_record = db.query(models.ImpactScore).filter(models.ImpactScore.equipment_id == eq.equipment_id).first()
        if not impact_record:
            impact_record = models.ImpactScore(equipment_id=eq.equipment_id)
            db.add(impact_record)
        impact_record.score = score
        impact_record.priority = priority
        impact_record.confidence = confidence
        impact_record.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        results.append(schemas.EquipmentImpactSummary(
            equipment_id=eq.equipment_id,
            equipment_type=eq.equipment_type,
            manufacturer=eq.manufacturer,
            department=eq.department,
            service=eq.service,
            status=eq.status,
            downtime_hours=eq.downtime_hours,
            criticality=eq.criticality,
            score=score,
            priority=priority,
            confidence=confidence,
            fallback_triggered=fallback_triggered,
            warnings_count=len(machine_warnings),
            freshness=freshness
        ))

    db.commit()
    # Sort by clinical impact score descending
    results.sort(key=lambda x: x.score, reverse=True)
    return results
