import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os
from pathlib import Path

# Setup
np.random.seed(42)
random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

NUM_EQUIPMENT = 100

def generate_services():
    services = [
        {"service_id": "SRV-ICU", "service_name": "ICU", "criticality": 100, "operating_hours": "24/7"},
        {"service_id": "SRV-ED", "service_name": "Emergency Department", "criticality": 100, "operating_hours": "24/7"},
        {"service_id": "SRV-OR", "service_name": "Operating Theatre", "criticality": 90, "operating_hours": "24/7"},
        {"service_id": "SRV-RAD", "service_name": "Radiology", "criticality": 75, "operating_hours": "24/7"},
        {"service_id": "SRV-CARD", "service_name": "Cardiology", "criticality": 80, "operating_hours": "08:00-18:00"},
        {"service_id": "SRV-OUT", "service_name": "Outpatient Department", "criticality": 40, "operating_hours": "08:00-18:00"},
    ]
    df = pd.DataFrame(services)
    df.to_csv(DATA_DIR / "services.csv", index=False)
    return df

def generate_equipment():
    types = ["Ventilator", "MRI", "CT Scanner", "ECG", "X-Ray", "Ultrasound", "Infusion Pump", "Patient Monitor", "Defibrillator", "Anesthesia Machine"]
    manufacturers = ["Manufacturer A", "Manufacturer B", "Manufacturer C", "Manufacturer D"]
    services = ["SRV-ICU", "SRV-ED", "SRV-OR", "SRV-RAD", "SRV-CARD", "SRV-OUT"]
    
    now = datetime.now()
    
    data = []
    for i in range(1, NUM_EQUIPMENT + 1):
        eq_type = random.choice(types)
        eq_id = f"EQ-{eq_type[:3].upper()}-{i:03d}"
        
        status = np.random.choice(["DOWN", "AVAILABLE", "MAINTENANCE"], p=[0.7, 0.2, 0.1])
        downtime_hours = round(random.uniform(1.0, 72.0), 1) if status == "DOWN" else 0.0
        downtime_start = (now - timedelta(hours=downtime_hours)).strftime("%Y-%m-%d %H:%M:%S") if status == "DOWN" else None
        
        data.append({
            "equipment_id": eq_id,
            "equipment_type": eq_type,
            "manufacturer": random.choice(manufacturers),
            "model": f"Model-{random.randint(100, 999)}",
            "department": random.choice(["Main Building", "Annex", "East Wing"]),
            "service": random.choice(services),
            "status": status,
            "downtime_start": downtime_start,
            "downtime_hours": downtime_hours,
            "criticality": random.choice(["HIGH", "MEDIUM", "LOW"]),
            "last_updated": (now - timedelta(minutes=random.randint(0, 1000))).strftime("%Y-%m-%d %H:%M:%S")
        })
    df = pd.DataFrame(data)
    df.to_csv(DATA_DIR / "equipment.csv", index=False)
    return df

def generate_procedures(equipment_df):
    urgency_levels = ["EMERGENCY", "URGENT", "ROUTINE"]
    
    now = datetime.now()
    data = []
    
    for _, eq in equipment_df.iterrows():
        # Generate 0 to 3 procedures per equipment
        num_procs = random.randint(0, 3)
        for p in range(num_procs):
            proc_id = f"PROC-{eq['equipment_id']}-{p+1}"
            scheduled_time = now + timedelta(hours=random.uniform(-2, 24))
            
            # Mix some stale data
            update_delta = random.randint(0, 10) # fresh
            if random.random() < 0.1:
                update_delta = random.randint(120, 600) # stale
                
            data.append({
                "procedure_id": proc_id,
                "procedure_type": f"Procedure-{random.randint(1, 50)}",
                "scheduled_time": scheduled_time.strftime("%Y-%m-%d %H:%M:%S"),
                "urgency": np.random.choice(urgency_levels, p=[0.2, 0.3, 0.5]),
                "required_equipment_id": eq["equipment_id"],
                "affected_service": eq["service"],
                "duration_minutes": random.choice([30, 60, 90, 120]),
                "status": "SCHEDULED",
                "last_updated": (now - timedelta(minutes=update_delta)).strftime("%Y-%m-%d %H:%M:%S")
            })
            
    df = pd.DataFrame(data)
    df.to_csv(DATA_DIR / "procedures.csv", index=False)
    return df

def generate_alternatives(equipment_df):
    data = []
    now = datetime.now()
    
    for _, eq in equipment_df.iterrows():
        avail = np.random.choice(["YES", "NO", "UNKNOWN"], p=[0.4, 0.5, 0.1])
        alt_id = f"EQ-ALT-{random.randint(100,999)}" if avail == "YES" else None
        
        # Mix some stale data
        update_delta = random.randint(0, 30)
        if random.random() < 0.15:
            update_delta = random.randint(300, 1000)
            
        data.append({
            "equipment_id": eq["equipment_id"],
            "alternative_available": avail,
            "alternative_equipment_id": alt_id,
            "capacity_available": random.choice([True, False]) if avail == "YES" else None,
            "last_updated": (now - timedelta(minutes=update_delta)).strftime("%Y-%m-%d %H:%M:%S")
        })
        
    df = pd.DataFrame(data)
    df.to_csv(DATA_DIR / "alternatives.csv", index=False)
    return df

def generate_repairs(equipment_df):
    data = []
    now = datetime.now()
    
    for _, eq in equipment_df.iterrows():
        if eq["status"] == "DOWN":
            est_hours = round(random.uniform(1.0, 48.0), 1)
            
            # Simulate missing estimate
            if random.random() < 0.05:
                est_hours = None
                
            data.append({
                "equipment_id": eq["equipment_id"],
                "estimated_repair_hours": est_hours,
                "repair_status": random.choice(["WAITING_PARTS", "TECHNICIAN_DISPATCHED", "DIAGNOSING"]),
                "estimated_completion": (now + timedelta(hours=est_hours)).strftime("%Y-%m-%d %H:%M:%S") if est_hours else None,
                "last_updated": (now - timedelta(minutes=random.randint(0, 60))).strftime("%Y-%m-%d %H:%M:%S")
            })
            
    df = pd.DataFrame(data)
    df.to_csv(DATA_DIR / "repairs.csv", index=False)
    return df

if __name__ == "__main__":
    print("Generating synthetic datasets...")
    generate_services()
    eq_df = generate_equipment()
    generate_procedures(eq_df)
    generate_alternatives(eq_df)
    generate_repairs(eq_df)
    print(f"Data generation complete. Saved to {DATA_DIR}")
