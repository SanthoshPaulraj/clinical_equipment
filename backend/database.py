from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from .config import settings

# For sqlite relative paths to work smoothly
db_url = settings.database_url
if db_url.startswith("sqlite:///./"):
    import pathlib
    base_dir = pathlib.Path(__file__).resolve().parent.parent
    db_path = base_dir / db_url.split("sqlite:///./")[1]
    db_url = f"sqlite:///{db_path}"

engine = create_engine(
    db_url, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
