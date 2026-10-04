from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from backend.database import get_db
from backend import models, schemas

router = APIRouter()

@router.post("/review")
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    # Role validation
    valid_roles = ["Biomedical Engineer", "Clinical Staff", "Clinical Manager", "Hospital Administrator"]
    if review.reviewer_role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}")

    # Check if override requires reason
    is_override = review.recommendation != review.human_decision
    if is_override and (not review.override_reason or review.override_reason.strip() == ""):
        raise HTTPException(status_code=422, detail="Override reason is mandatory when overriding system recommendation.")

    # Role Access Gating: Clinical Staff cannot override maintenance priority directly
    if review.reviewer_role == "Clinical Staff" and is_override and "Expedite" not in (review.override_reason or ""):
        raise HTTPException(
            status_code=403,
            detail="Role 'Clinical Staff' is authorized for clinical expedite requests only. Direct work order priority overrides require Biomedical Engineer or Manager authorization."
        )

    # 1. Save Human Review
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_review = models.HumanReview(
        equipment_id=review.equipment_id,
        recommendation=review.recommendation,
        human_decision=review.human_decision,
        reviewer_role=review.reviewer_role,
        timestamp=timestamp_str,
        review_comments=review.review_comments,
        override_reason=review.override_reason
    )
    db.add(db_review)
    
    # 2. Add to Audit Log
    event_type = f"HUMAN_REVIEW_{'OVERRIDE' if is_override else 'ACCEPT'}"
    if review.reviewer_role == "Clinical Staff":
        event_type = "CLINICAL_STAFF_EXPEDITE_REQUEST" if is_override else "CLINICAL_STAFF_CONFIRMATION"
    elif review.reviewer_role in ["Clinical Manager", "Hospital Administrator"]:
        event_type = "MANAGEMENT_OVERSIGHT_OVERRIDE" if is_override else "MANAGEMENT_OVERSIGHT_APPROVAL"

    audit_log = models.AuditLog(
        event_type=event_type,
        equipment_id=review.equipment_id,
        previous_priority=review.recommendation,
        new_priority=review.human_decision,
        user_role=review.reviewer_role,
        timestamp=timestamp_str,
        reason=review.review_comments,
        human_decision=review.human_decision,
        override_reason=review.override_reason
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "status": "success",
        "message": f"Review recorded successfully by {review.reviewer_role}",
        "event_type": event_type,
        "timestamp": timestamp_str
    }

@router.get("/reviews")
def get_reviews(equipment_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.HumanReview)
    if equipment_id:
        query = query.filter(models.HumanReview.equipment_id == equipment_id)
    return query.order_by(models.HumanReview.timestamp.desc()).all()

@router.get("/audit")
def get_audit_logs(equipment_id: Optional[str] = None, role: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.AuditLog)
    if equipment_id:
        query = query.filter(models.AuditLog.equipment_id == equipment_id)
    if role:
        query = query.filter(models.AuditLog.user_role == role)
    return query.order_by(models.AuditLog.timestamp.desc()).all()
