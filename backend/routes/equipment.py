from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import models, schemas

router = APIRouter()

@router.get("/equipment", response_model=List[schemas.EquipmentBase])
def read_equipment(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    equipment = db.query(models.Equipment).offset(skip).limit(limit).all()
    return equipment

@router.get("/equipment/{equipment_id}", response_model=schemas.EquipmentBase)
def read_equipment_by_id(equipment_id: str, db: Session = Depends(get_db)):
    db_equip = db.query(models.Equipment).filter(models.Equipment.equipment_id == equipment_id).first()
    if db_equip is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return db_equip
