from fastapi import FastAPI
from backend.routes import equipment, procedures, impact, reviews, metrics

app = FastAPI(title="Clinical-Impact-Aware Equipment Downtime API")

app.include_router(equipment.router, prefix="/api", tags=["equipment"])
app.include_router(procedures.router, prefix="/api", tags=["procedures"])
app.include_router(impact.router, prefix="/api", tags=["impact"])
app.include_router(reviews.router, prefix="/api", tags=["reviews"])
app.include_router(metrics.router, prefix="/api", tags=["metrics"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Clinical-Impact-Aware Equipment Downtime API"}
