import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path to import backend modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database import engine, Base
from backend.models import Equipment, Procedure, Alternative, Repair, Service

DATA_DIR = PROJECT_ROOT / "data"

def seed():
    print("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    
    print("Loading data from CSVs...")
    try:
        df_equip = pd.read_csv(DATA_DIR / "equipment.csv")
        df_proc = pd.read_csv(DATA_DIR / "procedures.csv")
        df_alt = pd.read_csv(DATA_DIR / "alternatives.csv")
        df_rep = pd.read_csv(DATA_DIR / "repairs.csv")
        df_srv = pd.read_csv(DATA_DIR / "services.csv")
    except FileNotFoundError as e:
        print(f"Error: {e}. Please run generate_dataset.py first.")
        return

    # Replace nan with None for DB insertion
    df_equip = df_equip.replace({float('nan'): None})
    df_proc = df_proc.replace({float('nan'): None})
    df_alt = df_alt.replace({float('nan'): None})
    df_rep = df_rep.replace({float('nan'): None})
    df_srv = df_srv.replace({float('nan'): None})

    print("Inserting data into database...")
    df_equip.to_sql("equipment", con=engine, if_exists="replace", index=False)
    df_proc.to_sql("procedures", con=engine, if_exists="replace", index=False)
    df_alt.to_sql("alternatives", con=engine, if_exists="replace", index=False)
    df_rep.to_sql("repairs", con=engine, if_exists="replace", index=False)
    df_srv.to_sql("services", con=engine, if_exists="replace", index=False)
    
    # We also need to make sure the tables for impact_scores, human_reviews, audit_logs exist
    # to_sql with if_exists="replace" might drop the SQLAlchemy schema constraints, 
    # so let's recreate the empty tables that weren't seeded from CSV.
    Base.metadata.create_all(bind=engine)

    print("Database seeding complete.")

if __name__ == "__main__":
    seed()
