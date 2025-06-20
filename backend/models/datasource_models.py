# backend/models/datasource_models.py - UPDATED
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from models.meta_models import Base  # Use the same Base as meta_models
import uuid
from datetime import datetime

class DataSource(Base):
    __tablename__ = 'data_sources'

    source_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_name = Column(String(128), nullable=False)
    source_type = Column(String(32), nullable=False)  # 'influxdb', 'parquet'
    connection_config = Column(Text, nullable=False)  # JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mappings = relationship("SourceMapping", back_populates="data_source", cascade="all, delete-orphan")

class SourceMapping(Base):
    __tablename__ = 'source_mappings'

    mapping_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String, ForeignKey("data_sources.source_id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipments.id"), nullable=False)
    
    # Source schema info
    measurement_name = Column(String(128), nullable=False)  # measurement/table name in source
    tag_mappings = Column(Text)  # JSON: {"n_rack": "rack", "n_bank": "bank"}
    field_mappings = Column(Text)  # JSON: {"n_soc": "soc", "n_soh": "soh"}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    data_source = relationship("DataSource", back_populates="mappings")

class SchemaCache(Base):
    __tablename__ = 'schema_cache'

    cache_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String, ForeignKey("data_sources.source_id"), nullable=False)
    schema_type = Column(String(32), nullable=False)  # 'measurements', 'tags', 'fields'
    schema_data = Column(Text, nullable=False)  # JSON string
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)