# backend/services/datasource_crud.py
from sqlalchemy.orm import Session
from models.datasource_models import DataSource, SourceMapping, SchemaCache
from datetime import datetime, timedelta
import json
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

# ---------- DataSource CRUD ----------
def create_data_source(db: Session, source_name: str, source_type: str, connection_config: dict) -> DataSource:
    """Create a new data source"""
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
        logger.info(f"Created data source: {data_source.source_id}")
        return data_source
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create data source: {str(e)}")
        raise Exception(f"Failed to create data source: {str(e)}")

def get_all_data_sources(db: Session) -> List[DataSource]:
    """Get all data sources"""
    try:
        return db.query(DataSource).order_by(DataSource.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Failed to get all data sources: {str(e)}")
        return []

def get_data_source_by_id(db: Session, source_id: str) -> Optional[DataSource]:
    """Get data source by ID"""
    try:
        return db.query(DataSource).filter(DataSource.source_id == source_id).first()
    except Exception as e:
        logger.error(f"Failed to get data source {source_id}: {str(e)}")
        return None

def get_active_data_sources(db: Session) -> List[DataSource]:
    """Get only active data sources"""
    try:
        return db.query(DataSource).filter(DataSource.is_active == True).order_by(DataSource.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Failed to get active data sources: {str(e)}")
        return []

def get_data_sources_by_type(db: Session, source_type: str) -> List[DataSource]:
    """Get data sources by type"""
    try:
        return db.query(DataSource).filter(DataSource.source_type == source_type).order_by(DataSource.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Failed to get data sources by type {source_type}: {str(e)}")
        return []

def update_data_source(db: Session, source_id: str, **kwargs) -> Optional[DataSource]:
    """Update data source"""
    try:
        data_source = db.query(DataSource).filter(DataSource.source_id == source_id).first()
        if data_source:
            for key, value in kwargs.items():
                if key == 'connection_config' and isinstance(value, dict):
                    value = json.dumps(value)
                if hasattr(data_source, key):
                    setattr(data_source, key, value)
            data_source.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(data_source)
            logger.info(f"Updated data source: {source_id}")
        return data_source
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update data source {source_id}: {str(e)}")
        return None

def delete_data_source(db: Session, source_id: str) -> Optional[DataSource]:
    """Delete data source and all related mappings"""
    try:
        data_source = db.query(DataSource).filter(DataSource.source_id == source_id).first()
        if data_source:
            # Delete all related mappings first
            db.query(SourceMapping).filter(SourceMapping.source_id == source_id).delete()
            # Delete all related cache entries
            db.query(SchemaCache).filter(SchemaCache.source_id == source_id).delete()
            # Delete the data source
            db.delete(data_source)
            db.commit()
            logger.info(f"Deleted data source: {source_id}")
        return data_source
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete data source {source_id}: {str(e)}")
        return None

def toggle_data_source_status(db: Session, source_id: str) -> Optional[DataSource]:
    """Toggle data source active status"""
    try:
        data_source = db.query(DataSource).filter(DataSource.source_id == source_id).first()
        if data_source:
            data_source.is_active = not data_source.is_active
            data_source.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(data_source)
            logger.info(f"Toggled data source {source_id} to {'active' if data_source.is_active else 'inactive'}")
        return data_source
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to toggle data source {source_id}: {str(e)}")
        return None

# ---------- SourceMapping CRUD ----------
def create_source_mapping(db: Session, source_id: str, equipment_id: int, 
                         measurement_name: str, tag_mappings: dict, field_mappings: dict) -> SourceMapping:
    """Create a new source mapping"""
    try:
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
        logger.info(f"Created mapping: {mapping.mapping_id}")
        return mapping
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create mapping: {str(e)}")
        raise Exception(f"Failed to create mapping: {str(e)}")

def get_all_mappings(db: Session) -> List[SourceMapping]:
    """Get all source mappings"""
    try:
        return db.query(SourceMapping).order_by(SourceMapping.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Failed to get all mappings: {str(e)}")
        return []

def get_mappings_by_source(db: Session, source_id: str) -> List[SourceMapping]:
    """Get all mappings for a data source"""
    try:
        return db.query(SourceMapping).filter(SourceMapping.source_id == source_id).order_by(SourceMapping.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Failed to get mappings for source {source_id}: {str(e)}")
        return []

def get_mappings_by_equipment(db: Session, equipment_id: int) -> List[SourceMapping]:
    """Get all mappings for an equipment"""
    try:
        return db.query(SourceMapping).filter(SourceMapping.equipment_id == equipment_id).order_by(SourceMapping.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Failed to get mappings for equipment {equipment_id}: {str(e)}")
        return []

def get_mapping_by_id(db: Session, mapping_id: str) -> Optional[SourceMapping]:
    """Get mapping by ID"""
    try:
        return db.query(SourceMapping).filter(SourceMapping.mapping_id == mapping_id).first()
    except Exception as e:
        logger.error(f"Failed to get mapping {mapping_id}: {str(e)}")
        return None

def get_mapping_by_source_and_measurement(db: Session, source_id: str, measurement_name: str) -> Optional[SourceMapping]:
    """Get mapping by source ID and measurement name"""
    try:
        return db.query(SourceMapping).filter(
            SourceMapping.source_id == source_id,
            SourceMapping.measurement_name == measurement_name
        ).first()
    except Exception as e:
        logger.error(f"Failed to get mapping for source {source_id} and measurement {measurement_name}: {str(e)}")
        return None

def update_source_mapping(db: Session, mapping_id: str, **kwargs) -> Optional[SourceMapping]:
    """Update source mapping"""
    try:
        mapping = db.query(SourceMapping).filter(SourceMapping.mapping_id == mapping_id).first()
        if mapping:
            for key, value in kwargs.items():
                if key in ['tag_mappings', 'field_mappings'] and isinstance(value, dict):
                    value = json.dumps(value)
                if hasattr(mapping, key):
                    setattr(mapping, key, value)
            mapping.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(mapping)
            logger.info(f"Updated mapping: {mapping_id}")
        return mapping
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update mapping {mapping_id}: {str(e)}")
        return None

def delete_source_mapping(db: Session, mapping_id: str) -> Optional[SourceMapping]:
    """Delete source mapping"""
    try:
        mapping = db.query(SourceMapping).filter(SourceMapping.mapping_id == mapping_id).first()
        if mapping:
            db.delete(mapping)
            db.commit()
            logger.info(f"Deleted mapping: {mapping_id}")
        return mapping
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete mapping {mapping_id}: {str(e)}")
        return None

def delete_mappings_by_source(db: Session, source_id: str) -> int:
    """Delete all mappings for a data source"""
    try:
        mappings = db.query(SourceMapping).filter(SourceMapping.source_id == source_id).all()
        count = len(mappings)
        for mapping in mappings:
            db.delete(mapping)
        db.commit()
        logger.info(f"Deleted {count} mappings for source {source_id}")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete mappings for source {source_id}: {str(e)}")
        return 0

def delete_mappings_by_equipment(db: Session, equipment_id: int) -> int:
    """Delete all mappings for an equipment"""
    try:
        mappings = db.query(SourceMapping).filter(SourceMapping.equipment_id == equipment_id).all()
        count = len(mappings)
        for mapping in mappings:
            db.delete(mapping)
        db.commit()
        logger.info(f"Deleted {count} mappings for equipment {equipment_id}")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete mappings for equipment {equipment_id}: {str(e)}")
        return 0

# ---------- SchemaCache CRUD ----------
def cache_schema(db: Session, source_id: str, schema_type: str, schema_data: dict, ttl_hours: int = 24) -> SchemaCache:
    """Cache schema discovery results"""
    try:
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
        logger.info(f"Cached {schema_type} schema for source {source_id}")
        return cache
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to cache schema: {str(e)}")
        raise Exception(f"Failed to cache schema: {str(e)}")

def get_cached_schema(db: Session, source_id: str, schema_type: str) -> Optional[Dict]:
    """Get cached schema if not expired"""
    try:
        cache = db.query(SchemaCache).filter(
            SchemaCache.source_id == source_id,
            SchemaCache.schema_type == schema_type,
            SchemaCache.expires_at > datetime.utcnow()
        ).first()
        
        if cache:
            logger.info(f"Found cached {schema_type} schema for source {source_id}")
            return json.loads(cache.schema_data)
        return None
    except Exception as e:
        logger.error(f"Failed to get cached schema: {str(e)}")
        return None

def get_all_cache_entries(db: Session) -> List[SchemaCache]:
    """Get all cache entries"""
    try:
        return db.query(SchemaCache).order_by(SchemaCache.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Failed to get cache entries: {str(e)}")
        return []

def clear_expired_cache(db: Session) -> int:
    """Clear expired cache entries"""
    try:
        expired = db.query(SchemaCache).filter(SchemaCache.expires_at <= datetime.utcnow()).all()
        count = len(expired)
        for cache in expired:
            db.delete(cache)
        db.commit()
        logger.info(f"Cleared {count} expired cache entries")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clear expired cache: {str(e)}")
        return 0

def clear_source_cache(db: Session, source_id: str) -> int:
    """Clear all cache entries for a source"""
    try:
        caches = db.query(SchemaCache).filter(SchemaCache.source_id == source_id).all()
        count = len(caches)
        for cache in caches:
            db.delete(cache)
        db.commit()
        logger.info(f"Cleared {count} cache entries for source {source_id}")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clear cache for source {source_id}: {str(e)}")
        return 0

def clear_all_cache(db: Session) -> int:
    """Clear all cache entries"""
    try:
        caches = db.query(SchemaCache).all()
        count = len(caches)
        for cache in caches:
            db.delete(cache)
        db.commit()
        logger.info(f"Cleared all {count} cache entries")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clear all cache: {str(e)}")
        return 0

# ---------- Advanced Query Functions ----------
def get_source_statistics(db: Session, source_id: str) -> Dict[str, Any]:
    """Get statistics for a data source"""
    try:
        source = get_data_source_by_id(db, source_id)
        if not source:
            return {}
        
        mappings = get_mappings_by_source(db, source_id)
        cache_entries = db.query(SchemaCache).filter(SchemaCache.source_id == source_id).all()
        
        return {
            "source_id": source_id,
            "source_name": source.source_name,
            "source_type": source.source_type,
            "is_active": source.is_active,
            "total_mappings": len(mappings),
            "total_cache_entries": len(cache_entries),
            "expired_cache_entries": len([c for c in cache_entries if c.expires_at <= datetime.utcnow()]),
            "created_at": source.created_at,
            "updated_at": source.updated_at
        }
    except Exception as e:
        logger.error(f"Failed to get statistics for source {source_id}: {str(e)}")
        return {}

def get_system_statistics(db: Session) -> Dict[str, Any]:
    """Get overall system statistics"""
    try:
        all_sources = get_all_data_sources(db)
        all_mappings = get_all_mappings(db)
        all_cache = get_all_cache_entries(db)
        
        source_types = {}
        for source in all_sources:
            source_types[source.source_type] = source_types.get(source.source_type, 0) + 1
        
        return {
            "total_sources": len(all_sources),
            "active_sources": len([s for s in all_sources if s.is_active]),
            "inactive_sources": len([s for s in all_sources if not s.is_active]),
            "total_mappings": len(all_mappings),
            "total_cache_entries": len(all_cache),
            "expired_cache_entries": len([c for c in all_cache if c.expires_at <= datetime.utcnow()]),
            "source_types": source_types,
            "last_updated": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Failed to get system statistics: {str(e)}")
        return {}

def search_data_sources(db: Session, search_term: str, source_type: Optional[str] = None, 
                       active_only: bool = False) -> List[DataSource]:
    """Search data sources by name or type"""
    try:
        query = db.query(DataSource)
        
        if search_term:
            query = query.filter(DataSource.source_name.ilike(f"%{search_term}%"))
        
        if source_type:
            query = query.filter(DataSource.source_type == source_type)
        
        if active_only:
            query = query.filter(DataSource.is_active == True)
        
        return query.order_by(DataSource.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Failed to search data sources: {str(e)}")
        return []

def validate_mapping_configuration(db: Session, mapping_id: str) -> Dict[str, Any]:
    """Validate mapping configuration"""
    try:
        mapping = get_mapping_by_id(db, mapping_id)
        if not mapping:
            return {"valid": False, "errors": ["Mapping not found"]}
        
        source = get_data_source_by_id(db, mapping.source_id)
        if not source:
            return {"valid": False, "errors": ["Data source not found"]}
        
        errors = []
        warnings = []
        
        # Check if tag and field mappings are valid JSON
        try:
            tag_mappings = json.loads(mapping.tag_mappings)
            field_mappings = json.loads(mapping.field_mappings)
        except json.JSONDecodeError:
            errors.append("Invalid JSON in mapping configuration")
            return {"valid": False, "errors": errors}
        
        # Check if mappings are not empty
        if not tag_mappings and not field_mappings:
            warnings.append("No tag or field mappings configured")
        
        # Check if measurement name is provided
        if not mapping.measurement_name:
            errors.append("Measurement name is required")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "mapping_id": mapping_id,
            "source_id": mapping.source_id,
            "equipment_id": mapping.equipment_id
        }
    except Exception as e:
        logger.error(f"Failed to validate mapping {mapping_id}: {str(e)}")
        return {"valid": False, "errors": [str(e)]}

# ---------- Batch Operations ----------
def bulk_create_mappings(db: Session, mappings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create multiple mappings in a single transaction"""
    try:
        created_mappings = []
        failed_mappings = []
        
        for mapping_data in mappings_data:
            try:
                mapping = create_source_mapping(
                    db,
                    mapping_data['source_id'],
                    mapping_data['equipment_id'],
                    mapping_data['measurement_name'],
                    mapping_data.get('tag_mappings', {}),
                    mapping_data.get('field_mappings', {})
                )
                created_mappings.append(mapping)
            except Exception as e:
                failed_mappings.append({
                    "data": mapping_data,
                    "error": str(e)
                })
        
        return {
            "total": len(mappings_data),
            "created": len(created_mappings),
            "failed": len(failed_mappings),
            "created_mappings": created_mappings,
            "failed_mappings": failed_mappings
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed bulk create mappings: {str(e)}")
        return {
            "total": len(mappings_data),
            "created": 0,
            "failed": len(mappings_data),
            "created_mappings": [],
            "failed_mappings": [{"error": str(e)}]
        }