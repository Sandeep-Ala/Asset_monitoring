# backend/config.py - UPDATED
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Import base classes
from models.meta_models import Base

BASE_PARQUET_PATH = "D:\Asset Monitoring System\Data-Backup\site=UK_Tollgate"

SQLITE_URL = "sqlite:///D:/Asset Monitoring System/GITHUB/Asset_monitoring/MetaDB.sqlite3"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# Import all models to ensure they're registered with Base
from models.meta_models import *
from models.datasource_models import *

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()