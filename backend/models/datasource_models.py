# models/datasource_models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

# Use the same Base from meta_models
from models.meta_models import Base

class DataConnection(Base):
    __tablename__ = "data_connections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable=False, unique=True)
    db_type = Column(String(32), nullable=False)  # sqlite3, influxdb, parquet
    description = Column(Text)
    status = Column(String(32), default="inactive")  # active, inactive, error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConnectionConfig(Base):
    __tablename__ = "connection_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    connection_id = Column(String, ForeignKey("data_connections.id"), nullable=False)
    config_key = Column(String(64), nullable=False)  # host, port, database, path, etc.
    config_value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)