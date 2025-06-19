# config.py
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.meta_models import Base

BASE_PARQUET_PATH = "D:\Asset Monitoring System\Data-Backup\site=UK_Tollgate"


SQLITE_URL = "sqlite:///D:/Asset Monitoring System/MetaDB.sqlite3"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()