from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./hospital_equipment.db"
    
    # Impact score weights (sum to 1.0)
    weight_urgency: float = 0.30
    weight_procedures_affected: float = 0.25
    weight_alternative_risk: float = 0.20
    weight_repair_time: float = 0.15
    weight_service_criticality: float = 0.10
    
    # Priority thresholds
    threshold_critical: int = 90
    threshold_high: int = 75
    threshold_medium: int = 50
    
    # Freshness thresholds in hours
    fresh_threshold: int = 1   # < 1 hour is FRESH
    stale_threshold: int = 6   # 1 to 6 hours is STALE; > 6 hours is VERY_STALE
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
