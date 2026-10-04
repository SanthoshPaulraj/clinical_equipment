from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any

class EquipmentBase(BaseModel):
    equipment_id: str
    equipment_type: str
    manufacturer: str
    model: str
    department: str
    service: str
    status: str
    downtime_start: Optional[str] = None
    downtime_hours: float
    criticality: str
    last_updated: str

    model_config = ConfigDict(from_attributes=True)

class ProcedureBase(BaseModel):
    procedure_id: str
    procedure_type: str
    scheduled_time: str
    urgency: str
    required_equipment_id: str
    affected_service: str
    duration_minutes: int
    status: str
    last_updated: str

    model_config = ConfigDict(from_attributes=True)

class AlternativeBase(BaseModel):
    equipment_id: str
    alternative_available: str
    alternative_equipment_id: Optional[str] = None
    capacity_available: Optional[bool] = None
    last_updated: str

    model_config = ConfigDict(from_attributes=True)

class RepairBase(BaseModel):
    equipment_id: str
    estimated_repair_hours: Optional[float] = None
    repair_status: str
    estimated_completion: Optional[str] = None
    last_updated: str

    model_config = ConfigDict(from_attributes=True)

class MachineWarning(BaseModel):
    code: str
    field: str
    status: str
    severity: str
    message: str
    action_required: str
    timestamp: Optional[str] = None

class ImpactExplanation(BaseModel):
    factors_increasing: List[str]
    factors_decreasing: List[str]
    missing_data_warnings: List[str]
    stale_data_warnings: List[str]
    fallback_triggered: bool

class ImpactResponse(BaseModel):
    equipment_id: str
    score: float
    priority: str
    confidence: str
    explanation: ImpactExplanation
    freshness: Dict[str, str]
    machine_warnings: List[MachineWarning] = []

class EquipmentImpactSummary(BaseModel):
    equipment_id: str
    equipment_type: str
    manufacturer: str
    department: str
    service: str
    status: str
    downtime_hours: float
    criticality: str
    score: float
    priority: str
    confidence: str
    fallback_triggered: bool
    warnings_count: int
    freshness: Dict[str, str]

class ReviewCreate(BaseModel):
    equipment_id: str
    recommendation: str
    human_decision: str
    reviewer_role: str
    review_comments: Optional[str] = None
    override_reason: Optional[str] = None

class AuditLogItem(BaseModel):
    audit_id: int
    event_type: str
    equipment_id: str
    previous_priority: Optional[str] = None
    new_priority: Optional[str] = None
    user_role: str
    timestamp: str
    reason: Optional[str] = None
    human_decision: Optional[str] = None
    override_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
