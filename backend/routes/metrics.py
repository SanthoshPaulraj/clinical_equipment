from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from backend.services.impact_engine import calculate_impact_score, get_priority_level

router = APIRouter()

@router.get("/dashboard/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    total_eq = db.query(models.Equipment).count()
    down_eq = db.query(models.Equipment).filter(models.Equipment.status == "DOWN").all()
    down_count = len(down_eq)
    
    # Check if impact scores exist
    impact_count = db.query(models.ImpactScore).count()
    
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    
    if impact_count > 0:
        critical_count = db.query(models.ImpactScore).filter(models.ImpactScore.priority == "CRITICAL").count()
        high_count = db.query(models.ImpactScore).filter(models.ImpactScore.priority == "HIGH").count()
        medium_count = db.query(models.ImpactScore).filter(models.ImpactScore.priority == "MEDIUM").count()
        low_count = db.query(models.ImpactScore).filter(models.ImpactScore.priority == "LOW").count()
    else:
        # Dynamically compute for down equipment
        all_alternatives = {a.equipment_id: a for a in db.query(models.Alternative).all()}
        all_repairs = {r.equipment_id: r for r in db.query(models.Repair).all()}
        all_services = {s.service_id: s for s in db.query(models.Service).all()}
        
        for eq in down_eq:
            procs = db.query(models.Procedure).filter(models.Procedure.required_equipment_id == eq.equipment_id).all()
            alt = all_alternatives.get(eq.equipment_id)
            rep = all_repairs.get(eq.equipment_id)
            srv = all_services.get(eq.service)
            
            score = calculate_impact_score(eq, procs, alt, rep, srv)
            priority = get_priority_level(score)
            
            if priority == "CRITICAL":
                critical_count += 1
            elif priority == "HIGH":
                high_count += 1
            elif priority == "MEDIUM":
                medium_count += 1
            else:
                low_count += 1

    affected_procs = db.query(models.Procedure).filter(models.Procedure.status == "SCHEDULED").count()
    services_count = db.query(models.Service).count()
    reviews_count = db.query(models.HumanReview).count()
    audit_count = db.query(models.AuditLog).count()
    
    return {
        "total_equipment": total_eq,
        "equipment_down": down_count,
        "critical": critical_count,
        "high": high_count,
        "medium": medium_count,
        "low": low_count,
        "procedures_affected": affected_procs,
        "services_affected": services_count,
        "human_reviews_completed": reviews_count,
        "audit_logs_total": audit_count
    }
