from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import models, schemas

router = APIRouter()

@router.get("/procedures", response_model=List[schemas.ProcedureBase])
def read_procedures(equipment_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.Procedure)
    if equipment_id:
        query = query.filter(models.Procedure.required_equipment_id == equipment_id)
    return query.offset(skip).limit(limit).all()
