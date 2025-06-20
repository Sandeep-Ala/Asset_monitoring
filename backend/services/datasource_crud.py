# backend/services/datasource_crud.py
from sqlalchemy.orm import Session
from models.datasource_models import DataSource, SourceMapping, SchemaCache
from datetime import datetime, timedelta
import json

# ---------- DataSource CRUD ----------
def create_data_source(db: Session, source_name: str, source_type: str, connection_config: dict):
    try:
        data_source = DataSource(
            source_name=source_name,
            source_type=source_type,
            connection_config=json.dumps(connection_config),
            is_active=True
        )
        db.add(data_source)
        db.commit()
        db.refresh(data_source)
        return data_source
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to create data source: {str(e)}")

def get_all_data_sources(db: Session):
    return db.query(DataSource).all()

def get_data_source_by_id(db: Session, source_id: str):
    return db.query(DataSource).filter(DataSource.source_id == source_id).first()

def get_active_data_sources(db: Session):
    return db.query(DataSource).filter(DataSource.is_active == True).all()

def update_data_source(db: Session, source_id: str, **kwargs):
    data_source = db.query(DataSource).filter(DataSource.source_id == source_id).first()
    if data_source:
        for key, value in kwargs.items():
            if key == 'connection_config' and isinstance(value, dict):
                value = json.dumps(value)
            setattr(data_source, key, value)
        data_source.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(data_source)
    return data_source

def delete_data_source(db: Session, source_id: str):
    data_source = db.query(DataSource).filter(DataSource.source_id == source_id).first()
    if data_source:
        db.delete(data_source)
        db.commit()
    return data_source

def toggle_data_source_status(db: Session, source_id: str):
    data_source = db.query(DataSource).filter(DataSource.source_id == source_id).first()
    if data_source:
        data_source.is_active = not data_source.is_active
        data_source.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(data_source)
    return data_source

# ---------- SourceMapping CRUD ----------
def create_source_mapping(db: Session, source_id: str, equipment_id: int, 
                         measurement_name: str, tag_mappings: dict, field_mappings: dict):
    mapping = SourceMapping(
        source_id=source_id,
        equipment_id=equipment_id,
        measurement_name=measurement_name,
        tag_mappings=json.dumps(tag_mappings),
        field_mappings=json.dumps(field_mappings)
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping

def get_mappings_by_source(db: Session, source_id: str):
    return db.query(SourceMapping).filter(SourceMapping.source_id == source_id).all()

def get_mappings_by_equipment(db: Session, equipment_id: int):
    return db.query(SourceMapping).filter(SourceMapping.equipment_id == equipment_id).all()

def get_mapping_by_id(db: Session, mapping_id: str):
    return db.query(SourceMapping).filter(SourceMapping.mapping_id == mapping_id).first()

def update_source_mapping(db: Session, mapping_id: str, **kwargs):
    mapping = db.query(SourceMapping).filter(SourceMapping.mapping_id == mapping_id).first()
    if mapping:
        for key, value in kwargs.items():
            if key in ['tag_mappings', 'field_mappings'] and isinstance(value, dict):
                value = json.dumps(value)
            setattr(mapping, key, value)
        mapping.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(mapping)
    return mapping

def delete_source_mapping(db: Session, mapping_id: str):
    mapping = db.query(SourceMapping).filter(SourceMapping.mapping_id == mapping_id).first()
    if mapping:
        db.delete(mapping)
        db.commit()
    return mapping

def delete_mappings_by_source(db: Session, source_id: str):
    mappings = db.query(SourceMapping).filter(SourceMapping.source_id == source_id).all()
    for mapping in mappings:
        db.delete(mapping)
    db.commit()
    return len(mappings)

# ---------- SchemaCache CRUD ----------
def cache_schema(db: Session, source_id: str, schema_type: str, schema_data: dict, ttl_hours: int = 24):
    expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
    
    # Delete existing cache for this source and type
    db.query(SchemaCache).filter(
        SchemaCache.source_id == source_id,
        SchemaCache.schema_type == schema_type
    ).delete()
    
    cache = SchemaCache(
        source_id=source_id,
        schema_type=schema_type,
        schema_data=json.dumps(schema_data),
        expires_at=expires_at
    )
    db.add(cache)
    db.commit()
    db.refresh(cache)
    return cache

def get_cached_schema(db: Session, source_id: str, schema_type: str):
    cache = db.query(SchemaCache).filter(
        SchemaCache.source_id == source_id,
        SchemaCache.schema_type == schema_type,
        SchemaCache.expires_at > datetime.utcnow()
    ).first()
    
    if cache:
        return json.loads(cache.schema_data)
    return None

def clear_expired_cache(db: Session):
    expired = db.query(SchemaCache).filter(SchemaCache.expires_at <= datetime.utcnow()).all()
    for cache in expired:
        db.delete(cache)
    db.commit()
    return len(expired)

def clear_source_cache(db: Session, source_id: str):
    caches = db.query(SchemaCache).filter(SchemaCache.source_id == source_id).all()
    for cache in caches:
        db.delete(cache)
    db.commit()
    return len(caches)