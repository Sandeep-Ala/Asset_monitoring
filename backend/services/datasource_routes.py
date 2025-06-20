# backend/services/datasource_routes.py - FIXED VERSION
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

import services.datasource_crud as crud
from services.discovery_services import get_discovery_service
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from config import get_db

datasource_router = InferringRouter()

# ---------- Pydantic Schemas - FIXED ----------
class DataSourceCreate(BaseModel):
    source_name: str
    source_type: str  # 'influxdb' or 'parquet'
    connection_config: Dict[str, Any]

class DataSourceUpdate(BaseModel):
    source_name: Optional[str] = None
    connection_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class DataSourceOut(BaseModel):
    source_id: str
    source_name: str
    source_type: str
    connection_config: str  # JSON string
    is_active: bool
    created_at: datetime  # Changed to datetime
    updated_at: datetime  # Changed to datetime
    
    class Config:
        from_attributes = True  # Updated for Pydantic v2
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ConnectionTestRequest(BaseModel):
    source_type: str
    connection_config: Dict[str, Any]

class DiscoveryRequest(BaseModel):
    source_type: str
    connection_config: Dict[str, Any]
    measurement: Optional[str] = None

class SourceMappingCreate(BaseModel):
    source_id: str
    equipment_id: int
    measurement_name: str
    tag_mappings: Dict[str, str]
    field_mappings: Dict[str, str]

class SourceMappingUpdate(BaseModel):
    measurement_name: Optional[str] = None
    tag_mappings: Optional[Dict[str, str]] = None
    field_mappings: Optional[Dict[str, str]] = None

class SourceMappingOut(BaseModel):
    mapping_id: str
    source_id: str
    equipment_id: int
    measurement_name: str
    tag_mappings: str  # JSON string
    field_mappings: str  # JSON string
    created_at: datetime  # Changed to datetime
    updated_at: datetime  # Changed to datetime
    
    class Config:
        from_attributes = True  # Updated for Pydantic v2
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# ---------- Data Source Routes ----------
@cbv(datasource_router)
class DataSourceRoutes:
    db: Session = Depends(get_db)
    datasource_router.tags = ["Data Sources"]
    datasource_router.prefix = "/datasources"

    @datasource_router.post("/", response_model=DataSourceOut)
    def create_data_source(self, data_source: DataSourceCreate):
        """Create a new data source"""
        try:
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
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create data source: {str(e)}")

    @datasource_router.get("/", response_model=List[DataSourceOut])
    def get_data_sources(self, active_only: bool = False):
        """Get all data sources"""
        if active_only:
            return crud.get_active_data_sources(self.db)
        return crud.get_all_data_sources(self.db)

    @datasource_router.get("/{source_id}", response_model=DataSourceOut)
    def get_data_source(self, source_id: str):
        """Get data source by ID"""
        data_source = crud.get_data_source_by_id(self.db, source_id)
        if not data_source:
            raise HTTPException(status_code=404, detail="Data source not found")
        return data_source

    @datasource_router.put("/{source_id}", response_model=DataSourceOut)
    def update_data_source(self, source_id: str, update_data: DataSourceUpdate):
        """Update data source"""
        updated = crud.update_data_source(self.db, source_id, **update_data.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Data source not found")
        return updated

    @datasource_router.delete("/{source_id}")
    def delete_data_source(self, source_id: str):
        """Delete data source"""
        deleted = crud.delete_data_source(self.db, source_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Data source not found")
        return {"message": "Data source deleted successfully"}

    @datasource_router.post("/{source_id}/toggle")
    def toggle_data_source(self, source_id: str):
        """Toggle data source active status"""
        toggled = crud.toggle_data_source_status(self.db, source_id)
        if not toggled:
            raise HTTPException(status_code=404, detail="Data source not found")
        return {"message": f"Data source {'activated' if toggled.is_active else 'deactivated'}"}

# ---------- Connection Testing Routes ----------
@cbv(datasource_router)
class ConnectionRoutes:
    datasource_router.tags = ["Connection Testing"]
    datasource_router.prefix = "/datasources"

    @datasource_router.post("/test-connection")
    def test_connection(self, request: ConnectionTestRequest):
        """Test data source connection"""
        try:
            # Handle connection config properly
            config_dict = request.connection_config
            if isinstance(config_dict, str):
                config_dict = json.loads(config_dict)
                
            discovery_service = get_discovery_service(request.source_type, config_dict)
            result = discovery_service.test_connection()
            return result
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection test failed: {str(e)}",
                "details": {"error": str(e)}
            }

# ---------- Discovery Routes ----------
@cbv(datasource_router)
class DiscoveryRoutes:
    db: Session = Depends(get_db)
    datasource_router.tags = ["Schema Discovery"]
    datasource_router.prefix = "/datasources"

    @datasource_router.post("/discover/measurements")
    def discover_measurements(self, request: DiscoveryRequest):
        """Discover available measurements/tables"""
        try:
            config_dict = request.connection_config
            if isinstance(config_dict, str):
                config_dict = json.loads(config_dict)
                
            discovery_service = get_discovery_service(request.source_type, config_dict)
            measurements = discovery_service.discover_measurements()
            return {"measurements": measurements}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Discovery failed: {str(e)}")

    @datasource_router.post("/discover/tags")
    def discover_tags(self, request: DiscoveryRequest):
        """Discover tag columns for a measurement"""
        if not request.measurement:
            raise HTTPException(status_code=400, detail="Measurement name is required")
        
        try:
            config_dict = request.connection_config
            if isinstance(config_dict, str):
                config_dict = json.loads(config_dict)
                
            discovery_service = get_discovery_service(request.source_type, config_dict)
            tags = discovery_service.discover_tags(request.measurement)
            return {"tags": tags}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Tag discovery failed: {str(e)}")

    @datasource_router.post("/discover/fields")
    def discover_fields(self, request: DiscoveryRequest):
        """Discover field columns for a measurement"""
        if not request.measurement:
            raise HTTPException(status_code=400, detail="Measurement name is required")
        
        try:
            config_dict = request.connection_config
            if isinstance(config_dict, str):
                config_dict = json.loads(config_dict)
                
            discovery_service = get_discovery_service(request.source_type, config_dict)
            fields = discovery_service.discover_fields(request.measurement)
            return {"fields": fields}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Field discovery failed: {str(e)}")

    @datasource_router.post("/discover/sample")
    def get_sample_data(self, request: DiscoveryRequest):
        """Get sample data from a measurement"""
        if not request.measurement:
            raise HTTPException(status_code=400, detail="Measurement name is required")
        
        try:
            config_dict = request.connection_config
            if isinstance(config_dict, str):
                config_dict = json.loads(config_dict)
                
            discovery_service = get_discovery_service(request.source_type, config_dict)
            sample_data = discovery_service.get_sample_data(request.measurement, limit=5)
            return {"sample_data": sample_data}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Sample data retrieval failed: {str(e)}")

    @datasource_router.get("/{source_id}/discover/measurements")
    def discover_measurements_by_id(self, source_id: str):
        """Discover measurements for an existing data source"""
        data_source = crud.get_data_source_by_id(self.db, source_id)
        if not data_source:
            raise HTTPException(status_code=404, detail="Data source not found")
        
        try:
            connection_config = json.loads(data_source.connection_config)
            discovery_service = get_discovery_service(data_source.source_type, connection_config)
            measurements = discovery_service.discover_measurements()
            
            # Cache the results
            crud.cache_schema(self.db, source_id, "measurements", {"measurements": measurements})
            
            return {"measurements": measurements}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Discovery failed: {str(e)}")

# ---------- Source Mapping Routes ----------
@cbv(datasource_router)
class SourceMappingRoutes:
    db: Session = Depends(get_db)
    datasource_router.tags = ["Source Mappings"]
    datasource_router.prefix = "/datasources"

    @datasource_router.post("/mappings", response_model=SourceMappingOut)
    def create_mapping(self, mapping: SourceMappingCreate):
        """Create a new source mapping"""
        return crud.create_source_mapping(
            self.db,
            mapping.source_id,
            mapping.equipment_id,
            mapping.measurement_name,
            mapping.tag_mappings,
            mapping.field_mappings
        )

    @datasource_router.get("/{source_id}/mappings", response_model=List[SourceMappingOut])
    def get_mappings_by_source(self, source_id: str):
        """Get all mappings for a data source"""
        return crud.get_mappings_by_source(self.db, source_id)

    @datasource_router.get("/mappings/equipment/{equipment_id}", response_model=List[SourceMappingOut])
    def get_mappings_by_equipment(self, equipment_id: int):
        """Get all mappings for an equipment"""
        return crud.get_mappings_by_equipment(self.db, equipment_id)

    @datasource_router.get("/mappings/{mapping_id}", response_model=SourceMappingOut)
    def get_mapping(self, mapping_id: str):
        """Get mapping by ID"""
        mapping = crud.get_mapping_by_id(self.db, mapping_id)
        if not mapping:
            raise HTTPException(status_code=404, detail="Mapping not found")
        return mapping

    @datasource_router.put("/mappings/{mapping_id}", response_model=SourceMappingOut)
    def update_mapping(self, mapping_id: str, update_data: SourceMappingUpdate):
        """Update source mapping"""
        updated = crud.update_source_mapping(self.db, mapping_id, **update_data.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Mapping not found")
        return updated

    @datasource_router.delete("/mappings/{mapping_id}")
    def delete_mapping(self, mapping_id: str):
        """Delete source mapping"""
        deleted = crud.delete_source_mapping(self.db, mapping_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Mapping not found")
        return {"message": "Mapping deleted successfully"}

    @datasource_router.delete("/{source_id}/mappings")
    def delete_all_mappings(self, source_id: str):
        """Delete all mappings for a data source"""
        count = crud.delete_mappings_by_source(self.db, source_id)
        return {"message": f"Deleted {count} mappings"}

# ---------- Batch Operations ----------
@cbv(datasource_router)
class BatchOperationRoutes:
    db: Session = Depends(get_db)
    datasource_router.tags = ["Batch Operations"]
    datasource_router.prefix = "/datasources"

    @datasource_router.post("/{source_id}/auto-map")
    def auto_map_measurements(self, source_id: str):
        """Automatically create mappings based on measurement names"""
        data_source = crud.get_data_source_by_id(self.db, source_id)
        if not data_source:
            raise HTTPException(status_code=404, detail="Data source not found")
        
        try:
            connection_config = json.loads(data_source.connection_config)
            discovery_service = get_discovery_service(data_source.source_type, connection_config)
            
            measurements = discovery_service.discover_measurements()
            created_mappings = []
            
            # Get existing equipments to match with
            from services.meta_crud import get_all_equipments
            equipments = get_all_equipments(self.db)
            equipment_names = {eq.name.lower(): eq for eq in equipments}
            
            for measurement in measurements:
                # Try to find matching equipment by name
                measurement_lower = measurement.lower()
                if measurement_lower in equipment_names:
                    equipment = equipment_names[measurement_lower]
                    
                    # Discover tags and fields for this measurement
                    tags = discovery_service.discover_tags(measurement)
                    fields = discovery_service.discover_fields(measurement)
                    
                    # Create basic mappings (can be customized later)
                    tag_mappings = {tag: tag for tag in tags}
                    field_mappings = {field['name']: field['name'] for field in fields}
                    
                    mapping = crud.create_source_mapping(
                        self.db,
                        source_id,
                        equipment.id,
                        measurement,
                        tag_mappings,
                        field_mappings
                    )
                    created_mappings.append(mapping)
            
            return {
                "message": f"Created {len(created_mappings)} auto-mappings",
                "mappings": created_mappings
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Auto-mapping failed: {str(e)}")

# Export router
router = datasource_router