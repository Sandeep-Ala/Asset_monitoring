# backend/services/datasource_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_utils.cbv import cbv
from sqlalchemy.orm import Session
from config import get_db
import json
import logging
from typing import List, Optional

# Import all schemas
from services.datasource_schemas import (
    ConnectionTestRequest, ConnectionTestResponse,
    DiscoveryRequest, MeasurementsResponse, TagsResponse, FieldsResponse, SampleDataResponse,
    DataSourceCreate, DataSourceUpdate, DataSourceOut,
    SourceMappingCreate, SourceMappingUpdate, SourceMappingOut,
    AutoMappingResponse, ErrorResponse
)

# Import CRUD operations
import services.datasource_crud as crud

# Import discovery services
from services.discovery_services import get_discovery_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
datasource_router = APIRouter(prefix="/datasources", tags=["DataSources"])

# ---------- Data Source Routes ----------
@cbv(datasource_router)
class DataSourceRoutes:
    db: Session = Depends(get_db)

    @datasource_router.post("/", response_model=DataSourceOut)
    def create_data_source(self, data_source: DataSourceCreate):
        """Create a new data source"""
        try:
            logger.info(f"Creating data source: {data_source.source_name}")
            
            # Ensure connection_config is properly handled
            config_dict = data_source.connection_config
            if isinstance(config_dict, str):
                config_dict = json.loads(config_dict)
            
            result = crud.create_data_source(
                self.db,
                data_source.source_name,
                data_source.source_type,
                config_dict
            )
            logger.info(f"Successfully created data source: {result.source_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create data source: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to create data source: {str(e)}")

    @datasource_router.get("/", response_model=List[DataSourceOut])
    def get_data_sources(self, 
                        active_only: bool = Query(False, description="Return only active sources"),
                        source_type: Optional[str] = Query(None, description="Filter by source type")):
        """Get all data sources with optional filtering"""
        try:
            if source_type:
                sources = crud.get_data_sources_by_type(self.db, source_type)
            elif active_only:
                sources = crud.get_active_data_sources(self.db)
            else:
                sources = crud.get_all_data_sources(self.db)
            
            logger.info(f"Retrieved {len(sources)} data sources")
            return sources
        except Exception as e:
            logger.error(f"Failed to get data sources: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve data sources: {str(e)}")

    @datasource_router.get("/{source_id}", response_model=DataSourceOut)
    def get_data_source(self, source_id: str):
        """Get data source by ID"""
        try:
            data_source = crud.get_data_source_by_id(self.db, source_id)
            if not data_source:
                raise HTTPException(status_code=404, detail="Data source not found")
            return data_source
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get data source {source_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve data source: {str(e)}")

    @datasource_router.put("/{source_id}", response_model=DataSourceOut)
    def update_data_source(self, source_id: str, update_data: DataSourceUpdate):
        """Update data source"""
        try:
            updated = crud.update_data_source(self.db, source_id, **update_data.dict(exclude_unset=True))
            if not updated:
                raise HTTPException(status_code=404, detail="Data source not found")
            logger.info(f"Updated data source: {source_id}")
            return updated
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update data source {source_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to update data source: {str(e)}")

    @datasource_router.delete("/{source_id}")
    def delete_data_source(self, source_id: str):
        """Delete data source"""
        try:
            deleted = crud.delete_data_source(self.db, source_id)
            if not deleted:
                raise HTTPException(status_code=404, detail="Data source not found")
            logger.info(f"Deleted data source: {source_id}")
            return {"message": "Data source deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete data source {source_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to delete data source: {str(e)}")

    @datasource_router.post("/{source_id}/toggle")
    def toggle_data_source(self, source_id: str):
        """Toggle data source active status"""
        try:
            toggled = crud.toggle_data_source_status(self.db, source_id)
            if not toggled:
                raise HTTPException(status_code=404, detail="Data source not found")
            status = 'activated' if toggled.is_active else 'deactivated'
            logger.info(f"Data source {source_id} {status}")
            return {"message": f"Data source {status}"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to toggle data source {source_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to toggle data source: {str(e)}")

# ---------- Connection Testing Routes ----------
@cbv(datasource_router)
class ConnectionRoutes:
    @datasource_router.post("/test-connection", response_model=ConnectionTestResponse)
    def test_connection(self, request: ConnectionTestRequest):
        """Test data source connection"""
        try:
            logger.info(f"Testing connection for {request.source_type}")
            
            # Handle connection config properly
            config_dict = request.connection_config
            if isinstance(config_dict, str):
                config_dict = json.loads(config_dict)
                
            discovery_service = get_discovery_service(request.source_type, config_dict)
            result = discovery_service.test_connection()
            
            logger.info(f"Connection test result: {result.get('success', False)}")
            return ConnectionTestResponse(**result)
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return ConnectionTestResponse(
                success=False,
                message=f"Connection test failed: {str(e)}",
                details={"error": str(e)}
            )

# ---------- Discovery Routes ----------
@cbv(datasource_router)
class DiscoveryRoutes:
    db: Session = Depends(get_db)

    @datasource_router.post("/discover/measurements", response_model=MeasurementsResponse)
    def discover_measurements(self, request: DiscoveryRequest):
        """Discover available measurements/tables"""
        try:
            logger.info(f"Discovering measurements for {request.source_type}")
            
            config_dict = request.connection_config
            if isinstance(config_dict, str):
                config_dict = json.loads(config_dict)
                
            discovery_service = get_discovery_service(request.source_type, config_dict)
            measurements = discovery_service.discover_measurements()
            
            logger.info(f"Found {len(measurements)} measurements")
            return MeasurementsResponse(measurements=measurements)
        except Exception as e:
            logger.error(f"Measurements discovery failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Discovery failed: {str(e)}")

    @datasource_router.post("/discover/tags", response_model=TagsResponse)
    def discover_tags(self, request: DiscoveryRequest):
        """Discover tag columns for a measurement"""
        if not request.measurement:
            raise HTTPException(status_code=400, detail="Measurement name is required")
        
        try:
            logger.info(f"Discovering tags for measurement: {request.measurement}")
            
            config_dict = request.connection_config
            if isinstance(config_dict, str):
                config_dict = json.loads(config_dict)
                
            discovery_service = get_discovery_service(request.source_type, config_dict)
            tags = discovery_service.discover_tags(request.measurement)
            
            logger.info(f"Found {len(tags)} tags for {request.measurement}")
            return TagsResponse(tags=tags)
        except Exception as e:
            logger.error(f"Tags discovery failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Tag discovery failed: {str(e)}")

    @datasource_router.post("/discover/fields", response_model=FieldsResponse)
    def discover_fields(self, request: DiscoveryRequest):
        """Discover field columns for a measurement"""
        if not request.measurement:
            raise HTTPException(status_code=400, detail="Measurement name is required")
        
        try:
            logger.info(f"Discovering fields for measurement: {request.measurement}")
            
            config_dict = request.connection_config
            if isinstance(config_dict, str):
                config_dict = json.loads(config_dict)
                
            discovery_service = get_discovery_service(request.source_type, config_dict)
            fields = discovery_service.discover_fields(request.measurement)
            
            logger.info(f"Found {len(fields)} fields for {request.measurement}")
            return FieldsResponse(fields=fields)
        except Exception as e:
            logger.error(f"Fields discovery failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Field discovery failed: {str(e)}")

    @datasource_router.post("/discover/sample", response_model=SampleDataResponse)
    def get_sample_data(self, request: DiscoveryRequest):
        """Get sample data from a measurement"""
        if not request.measurement:
            raise HTTPException(status_code=400, detail="Measurement name is required")
        
        try:
            logger.info(f"Getting sample data for measurement: {request.measurement}")
            
            config_dict = request.connection_config
            if isinstance(config_dict, str):
                config_dict = json.loads(config_dict)
                
            discovery_service = get_discovery_service(request.source_type, config_dict)
            sample_data = discovery_service.get_sample_data(request.measurement, limit=5)
            
            logger.info(f"Retrieved {len(sample_data)} sample records for {request.measurement}")
            return SampleDataResponse(sample_data=sample_data)
        except Exception as e:
            logger.error(f"Sample data retrieval failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Sample data retrieval failed: {str(e)}")

    @datasource_router.get("/{source_id}/discover/measurements", response_model=MeasurementsResponse)
    def discover_measurements_by_id(self, source_id: str):
        """Discover measurements for an existing data source"""
        try:
            data_source = crud.get_data_source_by_id(self.db, source_id)
            if not data_source:
                raise HTTPException(status_code=404, detail="Data source not found")
            
            logger.info(f"Discovering measurements for source: {source_id}")
            
            # Check cache first
            cached_data = crud.get_cached_schema(self.db, source_id, "measurements")
            if cached_data:
                logger.info(f"Using cached measurements for source: {source_id}")
                return MeasurementsResponse(measurements=cached_data.get("measurements", []))
            
            # Discover fresh data
            connection_config = json.loads(data_source.connection_config)
            discovery_service = get_discovery_service(data_source.source_type, connection_config)
            measurements = discovery_service.discover_measurements()
            
            # Cache the results
            crud.cache_schema(self.db, source_id, "measurements", {"measurements": measurements})
            
            logger.info(f"Found and cached {len(measurements)} measurements for source: {source_id}")
            return MeasurementsResponse(measurements=measurements)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Discovery failed for source {source_id}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Discovery failed: {str(e)}")

# ---------- Source Mapping Routes ----------
@cbv(datasource_router)
class SourceMappingRoutes:
    db: Session = Depends(get_db)

    @datasource_router.post("/mappings", response_model=SourceMappingOut)
    def create_mapping(self, mapping: SourceMappingCreate):
        """Create a new source mapping"""
        try:
            logger.info(f"Creating mapping for source {mapping.source_id} and equipment {mapping.equipment_id}")
            
            result = crud.create_source_mapping(
                self.db,
                mapping.source_id,
                mapping.equipment_id,
                mapping.measurement_name,
                mapping.tag_mappings,
                mapping.field_mappings
            )
            logger.info(f"Successfully created mapping: {result.mapping_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create mapping: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to create mapping: {str(e)}")

    @datasource_router.get("/{source_id}/mappings", response_model=List[SourceMappingOut])
    def get_mappings_by_source(self, source_id: str):
        """Get all mappings for a data source"""
        try:
            mappings = crud.get_mappings_by_source(self.db, source_id)
            logger.info(f"Retrieved {len(mappings)} mappings for source: {source_id}")
            return mappings
        except Exception as e:
            logger.error(f"Failed to get mappings for source {source_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve mappings: {str(e)}")

    @datasource_router.get("/mappings/equipment/{equipment_id}", response_model=List[SourceMappingOut])
    def get_mappings_by_equipment(self, equipment_id: int):
        """Get all mappings for an equipment"""
        try:
            mappings = crud.get_mappings_by_equipment(self.db, equipment_id)
            logger.info(f"Retrieved {len(mappings)} mappings for equipment: {equipment_id}")
            return mappings
        except Exception as e:
            logger.error(f"Failed to get mappings for equipment {equipment_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve mappings: {str(e)}")

    @datasource_router.get("/mappings/{mapping_id}", response_model=SourceMappingOut)
    def get_mapping(self, mapping_id: str):
        """Get mapping by ID"""
        try:
            mapping = crud.get_mapping_by_id(self.db, mapping_id)
            if not mapping:
                raise HTTPException(status_code=404, detail="Mapping not found")
            return mapping
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get mapping {mapping_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve mapping: {str(e)}")

    @datasource_router.put("/mappings/{mapping_id}", response_model=SourceMappingOut)
    def update_mapping(self, mapping_id: str, update_data: SourceMappingUpdate):
        """Update source mapping"""
        try:
            updated = crud.update_source_mapping(self.db, mapping_id, **update_data.dict(exclude_unset=True))
            if not updated:
                raise HTTPException(status_code=404, detail="Mapping not found")
            logger.info(f"Updated mapping: {mapping_id}")
            return updated
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update mapping {mapping_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to update mapping: {str(e)}")

    @datasource_router.delete("/mappings/{mapping_id}")
    def delete_mapping(self, mapping_id: str):
        """Delete source mapping"""
        try:
            deleted = crud.delete_source_mapping(self.db, mapping_id)
            if not deleted:
                raise HTTPException(status_code=404, detail="Mapping not found")
            logger.info(f"Deleted mapping: {mapping_id}")
            return {"message": "Mapping deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete mapping {mapping_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to delete mapping: {str(e)}")

    @datasource_router.delete("/{source_id}/mappings")
    def delete_all_mappings(self, source_id: str):
        """Delete all mappings for a data source"""
        try:
            count = crud.delete_mappings_by_source(self.db, source_id)
            logger.info(f"Deleted {count} mappings for source: {source_id}")
            return {"message": f"Deleted {count} mappings"}
        except Exception as e:
            logger.error(f"Failed to delete mappings for source {source_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to delete mappings: {str(e)}")

# ---------- Batch Operations ----------
@cbv(datasource_router)
class BatchOperationRoutes:
    db: Session = Depends(get_db)

    @datasource_router.post("/{source_id}/auto-map", response_model=AutoMappingResponse)
    def auto_map_measurements(self, source_id: str):
        """Automatically create mappings based on measurement names"""
        try:
            data_source = crud.get_data_source_by_id(self.db, source_id)
            if not data_source:
                raise HTTPException(status_code=404, detail="Data source not found")
            
            logger.info(f"Starting auto-mapping for source: {source_id}")
            
            connection_config = json.loads(data_source.connection_config)
            discovery_service = get_discovery_service(data_source.source_type, connection_config)
            
            measurements = discovery_service.discover_measurements()
            created_mappings = []
            failed_mappings = []
            
            # Get existing equipments to match with
            from services.meta_crud import get_all_equipments
            equipments = get_all_equipments(self.db)
            equipment_names = {eq.name.lower(): eq for eq in equipments}
            
            for measurement in measurements:
                try:
                    # Check if mapping already exists
                    existing_mapping = crud.get_mapping_by_source_and_measurement(
                        self.db, source_id, measurement
                    )
                    if existing_mapping:
                        logger.info(f"Mapping already exists for measurement: {measurement}")
                        continue
                    
                    # Try to find matching equipment by name
                    measurement_lower = measurement.lower()
                    if measurement_lower in equipment_names:
                        equipment = equipment_names[measurement_lower]
                        
                        # Discover tags and fields for this measurement
                        tags = discovery_service.discover_tags(measurement)
                        fields = discovery_service.discover_fields(measurement)
                        
                        # Create basic mappings (can be customized later)
                        tag_mappings = {tag: tag for tag in tags[:5]}  # Limit to first 5 tags
                        field_mappings = {field['name']: field['name'] for field in fields[:10]}  # Limit to first 10 fields
                        
                        mapping = crud.create_source_mapping(
                            self.db,
                            source_id,
                            equipment.id,
                            measurement,
                            tag_mappings,
                            field_mappings
                        )
                        created_mappings.append(mapping)
                        logger.info(f"Created auto-mapping for measurement: {measurement}")
                    else:
                        failed_mappings.append({
                            "measurement": measurement,
                            "reason": f"No matching equipment found for '{measurement}'"
                        })
                        
                except Exception as e:
                    logger.error(f"Failed to create mapping for {measurement}: {str(e)}")
                    failed_mappings.append({
                        "measurement": measurement,
                        "reason": str(e)
                    })
            
            logger.info(f"Auto-mapping completed: {len(created_mappings)} created, {len(failed_mappings)} failed")
            
            return AutoMappingResponse(
                message=f"Created {len(created_mappings)} auto-mappings",
                mappings=created_mappings,
                failed=failed_mappings
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Auto-mapping failed for source {source_id}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Auto-mapping failed: {str(e)}")

# ---------- Statistics and Utilities ----------
@cbv(datasource_router)
class UtilityRoutes:
    db: Session = Depends(get_db)

    @datasource_router.get("/{source_id}/statistics")
    def get_source_statistics(self, source_id: str):
        """Get statistics for a data source"""
        try:
            stats = crud.get_source_statistics(self.db, source_id)
            if not stats:
                raise HTTPException(status_code=404, detail="Data source not found")
            return stats
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get statistics for source {source_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

    @datasource_router.get("/system/statistics")
    def get_system_statistics(self):
        """Get overall system statistics"""
        try:
            stats = crud.get_system_statistics(self.db)
            return stats
        except Exception as e:
            logger.error(f"Failed to get system statistics: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

    @datasource_router.post("/cache/clear")
    def clear_cache(self, source_id: Optional[str] = Query(None, description="Specific source ID to clear cache for")):
        """Clear schema cache"""
        try:
            if source_id:
                count = crud.clear_source_cache(self.db, source_id)
                message = f"Cleared {count} cache entries for source {source_id}"
            else:
                count = crud.clear_expired_cache(self.db)
                message = f"Cleared {count} expired cache entries"
            
            logger.info(message)
            return {"message": message, "cleared_entries": count}
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

    @datasource_router.get("/search", response_model=List[DataSourceOut])
    def search_data_sources(self, 
                           q: str = Query(..., description="Search term"),
                           source_type: Optional[str] = Query(None, description="Filter by source type"),
                           active_only: bool = Query(False, description="Only active sources")):
        """Search data sources"""
        try:
            sources = crud.search_data_sources(self.db, q, source_type, active_only)
            logger.info(f"Found {len(sources)} sources matching search: {q}")
            return sources
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    @datasource_router.get("/mappings/{mapping_id}/validate")
    def validate_mapping(self, mapping_id: str):
        """Validate mapping configuration"""
        try:
            validation_result = crud.validate_mapping_configuration(self.db, mapping_id)
            return validation_result
        except Exception as e:
            logger.error(f"Validation failed for mapping {mapping_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

# ---------- Advanced Operations ----------
@cbv(datasource_router)
class AdvancedOperationRoutes:
    db: Session = Depends(get_db)

    @datasource_router.post("/bulk/create-mappings")
    def bulk_create_mappings(self, mappings_data: List[SourceMappingCreate]):
        """Create multiple mappings in bulk"""
        try:
            logger.info(f"Creating {len(mappings_data)} mappings in bulk")
            
            mappings_dict_list = []
            for mapping in mappings_data:
                mappings_dict_list.append({
                    'source_id': mapping.source_id,
                    'equipment_id': mapping.equipment_id,
                    'measurement_name': mapping.measurement_name,
                    'tag_mappings': mapping.tag_mappings,
                    'field_mappings': mapping.field_mappings
                })
            
            result = crud.bulk_create_mappings(self.db, mappings_dict_list)
            logger.info(f"Bulk creation completed: {result['created']} created, {result['failed']} failed")
            
            return result
        except Exception as e:
            logger.error(f"Bulk create mappings failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Bulk create failed: {str(e)}")

    @datasource_router.post("/{source_id}/sync")
    def sync_source_schema(self, source_id: str, force_refresh: bool = Query(False, description="Force refresh cache")):
        """Synchronize source schema and update cache"""
        try:
            data_source = crud.get_data_source_by_id(self.db, source_id)
            if not data_source:
                raise HTTPException(status_code=404, detail="Data source not found")
            
            logger.info(f"Synchronizing schema for source: {source_id}")
            
            # Clear cache if force refresh
            if force_refresh:
                crud.clear_source_cache(self.db, source_id)
            
            connection_config = json.loads(data_source.connection_config)
            discovery_service = get_discovery_service(data_source.source_type, connection_config)
            
            # Discover and cache all schema elements
            measurements = discovery_service.discover_measurements()
            crud.cache_schema(self.db, source_id, "measurements", {"measurements": measurements})
            
            # Discover schema for each measurement
            schema_details = {}
            for measurement in measurements[:5]:  # Limit to first 5 for performance
                try:
                    tags = discovery_service.discover_tags(measurement)
                    fields = discovery_service.discover_fields(measurement)
                    
                    schema_details[measurement] = {
                        "tags": tags,
                        "fields": fields
                    }
                except Exception as e:
                    logger.warning(f"Failed to discover schema for {measurement}: {str(e)}")
            
            # Cache detailed schema
            crud.cache_schema(self.db, source_id, "detailed_schema", schema_details)
            
            logger.info(f"Schema synchronization completed for source: {source_id}")
            
            return {
                "message": "Schema synchronized successfully",
                "measurements_count": len(measurements),
                "detailed_measurements": len(schema_details),
                "force_refresh": force_refresh
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Schema sync failed for source {source_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Schema synchronization failed: {str(e)}")

    @datasource_router.get("/{source_id}/health")
    def check_source_health(self, source_id: str):
        """Check health status of a data source"""
        try:
            data_source = crud.get_data_source_by_id(self.db, source_id)
            if not data_source:
                raise HTTPException(status_code=404, detail="Data source not found")
            
            logger.info(f"Checking health for source: {source_id}")
            
            connection_config = json.loads(data_source.connection_config)
            discovery_service = get_discovery_service(data_source.source_type, connection_config)
            
            # Test connection
            connection_result = discovery_service.test_connection()
            
            # Get basic statistics
            stats = crud.get_source_statistics(self.db, source_id)
            
            # Check cache status
            cache_entries = crud.get_all_cache_entries(self.db)
            source_cache = [c for c in cache_entries if c.source_id == source_id]
            
            health_status = {
                "source_id": source_id,
                "source_name": data_source.source_name,
                "source_type": data_source.source_type,
                "is_active": data_source.is_active,
                "connection_status": connection_result,
                "statistics": stats,
                "cache_entries": len(source_cache),
                "last_updated": data_source.updated_at.isoformat() if data_source.updated_at else None,
                "health_check_time": "2025-01-20T00:00:00Z"
            }
            
            return health_status
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Health check failed for source {source_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

    @datasource_router.post("/export")
    def export_configurations(self, source_ids: Optional[List[str]] = None, include_configs: bool = False):
        """Export data source configurations"""
        try:
            logger.info(f"Exporting configurations for sources: {source_ids or 'all'}")
            
            if source_ids:
                sources = []
                for source_id in source_ids:
                    source = crud.get_data_source_by_id(self.db, source_id)
                    if source:
                        sources.append(source)
            else:
                sources = crud.get_all_data_sources(self.db)
            
            export_data = {
                "export_timestamp": "2025-01-20T00:00:00Z",
                "total_sources": len(sources),
                "sources": []
            }
            
            for source in sources:
                source_data = {
                    "source_id": source.source_id,
                    "source_name": source.source_name,
                    "source_type": source.source_type,
                    "is_active": source.is_active,
                    "created_at": source.created_at.isoformat() if source.created_at else None,
                    "updated_at": source.updated_at.isoformat() if source.updated_at else None
                }
                
                # Include connection configs if requested (be careful with sensitive data)
                if include_configs:
                    source_data["connection_config"] = source.connection_config
                
                # Get mappings for this source
                mappings = crud.get_mappings_by_source(self.db, source.source_id)
                source_data["mappings"] = []
                
                for mapping in mappings:
                    mapping_data = {
                        "mapping_id": mapping.mapping_id,
                        "equipment_id": mapping.equipment_id,
                        "measurement_name": mapping.measurement_name,
                        "tag_mappings": mapping.tag_mappings,
                        "field_mappings": mapping.field_mappings,
                        "created_at": mapping.created_at.isoformat() if mapping.created_at else None
                    }
                    source_data["mappings"].append(mapping_data)
                
                export_data["sources"].append(source_data)
            
            logger.info(f"Exported {len(sources)} data source configurations")
            return export_data
            
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

    @datasource_router.post("/import")
    def import_configurations(self, import_data: dict, overwrite_existing: bool = False):
        """Import data source configurations"""
        try:
            logger.info(f"Importing data source configurations")
            
            sources_data = import_data.get("sources", [])
            import_results = {
                "total_sources": len(sources_data),
                "imported_sources": 0,
                "imported_mappings": 0,
                "skipped_sources": 0,
                "failed_sources": 0,
                "errors": []
            }
            
            for source_data in sources_data:
                try:
                    source_id = source_data.get("source_id")
                    
                    # Check if source already exists
                    existing_source = crud.get_data_source_by_id(self.db, source_id) if source_id else None
                    
                    if existing_source and not overwrite_existing:
                        import_results["skipped_sources"] += 1
                        logger.info(f"Skipped existing source: {source_id}")
                        continue
                    
                    # Create or update source
                    if existing_source and overwrite_existing:
                        # Update existing source
                        updates = {
                            "source_name": source_data.get("source_name"),
                            "is_active": source_data.get("is_active", True)
                        }
                        if source_data.get("connection_config"):
                            updates["connection_config"] = json.loads(source_data["connection_config"])
                        
                        crud.update_data_source(self.db, source_id, **updates)
                        import_results["imported_sources"] += 1
                    else:
                        # Create new source
                        connection_config = json.loads(source_data.get("connection_config", "{}"))
                        new_source = crud.create_data_source(
                            self.db,
                            source_data["source_name"],
                            source_data["source_type"],
                            connection_config
                        )
                        source_id = new_source.source_id
                        import_results["imported_sources"] += 1
                    
                    # Import mappings
                    mappings_data = source_data.get("mappings", [])
                    for mapping_data in mappings_data:
                        try:
                            # Check if mapping already exists
                            existing_mapping = crud.get_mapping_by_source_and_measurement(
                                self.db, source_id, mapping_data["measurement_name"]
                            )
                            
                            if existing_mapping and not overwrite_existing:
                                continue
                            
                            if existing_mapping and overwrite_existing:
                                # Update existing mapping
                                updates = {
                                    "tag_mappings": json.loads(mapping_data.get("tag_mappings", "{}")),
                                    "field_mappings": json.loads(mapping_data.get("field_mappings", "{}"))
                                }
                                crud.update_source_mapping(self.db, existing_mapping.mapping_id, **updates)
                            else:
                                # Create new mapping
                                crud.create_source_mapping(
                                    self.db,
                                    source_id,
                                    mapping_data["equipment_id"],
                                    mapping_data["measurement_name"],
                                    json.loads(mapping_data.get("tag_mappings", "{}")),
                                    json.loads(mapping_data.get("field_mappings", "{}"))
                                )
                            
                            import_results["imported_mappings"] += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to import mapping: {str(e)}")
                            import_results["errors"].append(f"Mapping import failed: {str(e)}")
                    
                except Exception as e:
                    logger.error(f"Failed to import source: {str(e)}")
                    import_results["failed_sources"] += 1
                    import_results["errors"].append(f"Source import failed: {str(e)}")
            
            logger.info(f"Import completed: {import_results}")
            return import_results
            
        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

# ---------- Maintenance Operations ----------
@cbv(datasource_router)
class MaintenanceRoutes:
    db: Session = Depends(get_db)

    @datasource_router.post("/maintenance/cleanup")
    def cleanup_resources(self, 
                         clear_expired_cache: bool = Query(True, description="Clear expired cache entries"),
                         validate_mappings: bool = Query(True, description="Validate all mappings"),
                         check_connections: bool = Query(False, description="Check all connections")):
        """Perform maintenance operations"""
        try:
            logger.info("Starting maintenance operations")
            
            maintenance_results = {
                "timestamp": "2025-01-20T00:00:00Z",
                "operations_performed": [],
                "results": {}
            }
            
            # Clear expired cache
            if clear_expired_cache:
                expired_count = crud.clear_expired_cache(self.db)
                maintenance_results["operations_performed"].append("clear_expired_cache")
                maintenance_results["results"]["expired_cache_cleared"] = expired_count
                logger.info(f"Cleared {expired_count} expired cache entries")
            
            # Validate mappings
            if validate_mappings:
                all_mappings = crud.get_all_mappings(self.db)
                validation_results = {
                    "total_mappings": len(all_mappings),
                    "valid_mappings": 0,
                    "invalid_mappings": 0,
                    "validation_errors": []
                }
                
                for mapping in all_mappings:
                    try:
                        validation = crud.validate_mapping_configuration(self.db, mapping.mapping_id)
                        if validation.get("valid", False):
                            validation_results["valid_mappings"] += 1
                        else:
                            validation_results["invalid_mappings"] += 1
                            validation_results["validation_errors"].append({
                                "mapping_id": mapping.mapping_id,
                                "errors": validation.get("errors", [])
                            })
                    except Exception as e:
                        validation_results["invalid_mappings"] += 1
                        validation_results["validation_errors"].append({
                            "mapping_id": mapping.mapping_id,
                            "errors": [str(e)]
                        })
                
                maintenance_results["operations_performed"].append("validate_mappings")
                maintenance_results["results"]["mapping_validation"] = validation_results
                logger.info(f"Validated {len(all_mappings)} mappings")
            
            # Check connections
            if check_connections:
                all_sources = crud.get_all_data_sources(self.db)
                connection_results = {
                    "total_sources": len(all_sources),
                    "healthy_sources": 0,
                    "unhealthy_sources": 0,
                    "connection_errors": []
                }
                
                for source in all_sources:
                    try:
                        connection_config = json.loads(source.connection_config)
                        discovery_service = get_discovery_service(source.source_type, connection_config)
                        result = discovery_service.test_connection()
                        
                        if result.get("success", False):
                            connection_results["healthy_sources"] += 1
                        else:
                            connection_results["unhealthy_sources"] += 1
                            connection_results["connection_errors"].append({
                                "source_id": source.source_id,
                                "source_name": source.source_name,
                                "error": result.get("message", "Unknown error")
                            })
                    except Exception as e:
                        connection_results["unhealthy_sources"] += 1
                        connection_results["connection_errors"].append({
                            "source_id": source.source_id,
                            "source_name": source.source_name,
                            "error": str(e)
                        })
                
                maintenance_results["operations_performed"].append("check_connections")
                maintenance_results["results"]["connection_check"] = connection_results
                logger.info(f"Checked {len(all_sources)} data source connections")
            
            logger.info("Maintenance operations completed")
            return maintenance_results
            
        except Exception as e:
            logger.error(f"Maintenance failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Maintenance failed: {str(e)}")

    @datasource_router.get("/maintenance/status")
    def get_maintenance_status(self):
        """Get system maintenance status and recommendations"""
        try:
            logger.info("Getting maintenance status")
            
            # Get system statistics
            stats = crud.get_system_statistics(self.db)
            
            # Get cache information
            all_cache = crud.get_all_cache_entries(self.db)
            expired_cache = [c for c in all_cache if c.expires_at <= "2025-01-20T00:00:00Z"]
            
            # Check for inactive sources
            inactive_sources = crud.get_all_data_sources(self.db)
            inactive_count = len([s for s in inactive_sources if not s.is_active])
            
            # Generate recommendations
            recommendations = []
            
            if len(expired_cache) > 0:
                recommendations.append(f"Clear {len(expired_cache)} expired cache entries")
            
            if inactive_count > 0:
                recommendations.append(f"Review {inactive_count} inactive data sources")
            
            if stats.get("total_mappings", 0) == 0:
                recommendations.append("No mappings found - consider creating mappings for data sources")
            
            maintenance_status = {
                "system_health": "healthy" if len(recommendations) == 0 else "needs_attention",
                "last_check": "2025-01-20T00:00:00Z",
                "statistics": stats,
                "cache_status": {
                    "total_entries": len(all_cache),
                    "expired_entries": len(expired_cache)
                },
                "recommendations": recommendations,
                "maintenance_needed": len(recommendations) > 0
            }
            
            return maintenance_status
            
        except Exception as e:
            logger.error(f"Failed to get maintenance status: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get maintenance status: {str(e)}")

# Export router
router = datasource_router