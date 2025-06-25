# config.py (Updated)

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.meta_models import Base
# Import new models to ensure they're registered
from models.datasource_models import DataConnection, ConnectionConfig

BASE_PARQUET_PATH = "D:\Asset Monitoring System\Data-Backup\site=UK_Tollgate"

SQLITE_URL = "sqlite:///D:/Asset Monitoring System/GITHUB/Asset_monitoring/MetaDB.sqlite3"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# Create all tables (including new datasource tables)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()