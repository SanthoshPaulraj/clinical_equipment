from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime
from .database import Base

class Equipment(Base):
    __tablename__ = "equipment"
    equipment_id = Column(String, primary_key=True, index=True)
    equipment_type = Column(String)
    manufacturer = Column(String)
    model = Column(String)
    department = Column(String)
    service = Column(String)
    status = Column(String)
    downtime_start = Column(String, nullable=True)
    downtime_hours = Column(Float, default=0.0)
    criticality = Column(String)
    last_updated = Column(String)

class Procedure(Base):
    __tablename__ = "procedures"
    procedure_id = Column(String, primary_key=True, index=True)
    procedure_type = Column(String)
    scheduled_time = Column(String)
    urgency = Column(String)
    required_equipment_id = Column(String)
    affected_service = Column(String)
    duration_minutes = Column(Integer)
    status = Column(String)
    last_updated = Column(String)

class Alternative(Base):
    __tablename__ = "alternatives"
    equipment_id = Column(String, primary_key=True, index=True)
    alternative_available = Column(String)
    alternative_equipment_id = Column(String, nullable=True)
    capacity_available = Column(Boolean, nullable=True)
    last_updated = Column(String)

class Repair(Base):
    __tablename__ = "repairs"
    equipment_id = Column(String, primary_key=True, index=True)
    estimated_repair_hours = Column(Float, nullable=True)
    repair_status = Column(String)
    estimated_completion = Column(String, nullable=True)
    last_updated = Column(String)

class Service(Base):
    __tablename__ = "services"
    service_id = Column(String, primary_key=True, index=True)
    service_name = Column(String)
    criticality = Column(Integer)
    operating_hours = Column(String)

class ImpactScore(Base):
    __tablename__ = "impact_scores"
    equipment_id = Column(String, primary_key=True, index=True)
    score = Column(Float)
    priority = Column(String)
    confidence = Column(String)
    explanation = Column(String)
    last_updated = Column(String)

class HumanReview(Base):
    __tablename__ = "human_reviews"
    review_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equipment_id = Column(String, index=True)
    recommendation = Column(String)
    human_decision = Column(String)
    reviewer_role = Column(String)
    timestamp = Column(String)
    review_comments = Column(String, nullable=True)
    override_reason = Column(String, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    audit_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_type = Column(String)
    equipment_id = Column(String)
    previous_priority = Column(String, nullable=True)
    new_priority = Column(String, nullable=True)
    user_role = Column(String)
    timestamp = Column(String)
    reason = Column(String, nullable=True)
    human_decision = Column(String, nullable=True)
    override_reason = Column(String, nullable=True)
