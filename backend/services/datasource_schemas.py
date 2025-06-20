# backend/services/datasource_schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Base configuration
class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )

# ---------- Request Models ----------
class ConnectionTestRequest(BaseModel):
    """Request model for testing data source connections"""
    source_type: str = Field(..., description="Type of data source", examples=["influxdb", "parquet"])
    connection_config: Union[Dict[str, Any], str] = Field(..., description="Connection configuration")

class DiscoveryRequest(BaseModel):
    """Request model for schema discovery operations"""
    source_type: str = Field(..., description="Type of data source")
    connection_config: Union[Dict[str, Any], str] = Field(..., description="Connection configuration")
    measurement: Optional[str] = Field(None, description="Measurement name for tag/field discovery")

class DataSourceCreate(BaseModel):
    """Request model for creating a new data source"""
    source_name: str = Field(..., min_length=1, max_length=128, description="Human-readable name")
    source_type: str = Field(..., description="Type of data source")
    connection_config: Union[Dict[str, Any], str] = Field(..., description="Connection configuration")

class DataSourceUpdate(BaseModel):
    """Request model for updating an existing data source"""
    source_name: Optional[str] = Field(None, min_length=1, max_length=128)
    connection_config: Optional[Union[Dict[str, Any], str]] = None
    is_active: Optional[bool] = None

class SourceMappingCreate(BaseModel):
    """Request model for creating a new source mapping"""
    source_id: str = Field(..., description="Data source ID")
    equipment_id: int = Field(..., description="Equipment ID")
    measurement_name: str = Field(..., description="Measurement/table name in source")
    tag_mappings: Dict[str, str] = Field(default_factory=dict, description="Tag field mappings")
    field_mappings: Dict[str, str] = Field(default_factory=dict, description="Value field mappings")

class SourceMappingUpdate(BaseModel):
    """Request model for updating an existing source mapping"""
    equipment_id: Optional[int] = None
    measurement_name: Optional[str] = None
    tag_mappings: Optional[Dict[str, str]] = None
    field_mappings: Optional[Dict[str, str]] = None

# ---------- Response Models ----------
class ConnectionTestResponse(BaseModel):
    """Response model for connection test results"""
    success: bool = Field(..., description="Whether connection was successful")
    message: str = Field(..., description="Human-readable result message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional connection details")

class DiscoveryResponse(BaseModel):
    """Base response model for discovery operations"""
    success: bool = Field(default=True, description="Whether discovery was successful")
    message: Optional[str] = Field(None, description="Result message")

class MeasurementsResponse(DiscoveryResponse):
    """Response model for measurements discovery"""
    measurements: List[str] = Field(default_factory=list, description="List of available measurements")

class TagsResponse(DiscoveryResponse):
    """Response model for tags discovery"""
    tags: List[str] = Field(default_factory=list, description="List of available tag keys")

class FieldInfo(BaseModel):
    """Field information with name and type"""
    name: str = Field(..., description="Field name")
    type: str = Field(..., description="Field data type")

class FieldsResponse(DiscoveryResponse):
    """Response model for fields discovery"""
    fields: List[FieldInfo] = Field(default_factory=list, description="List of available fields with types")

class SampleDataResponse(DiscoveryResponse):
    """Response model for sample data"""
    sample_data: List[Dict[str, Any]] = Field(default_factory=list, description="Sample data records")

class DataSourceOut(BaseSchema):
    """Response model for data source information"""
    source_id: str = Field(..., description="Unique source identifier")
    source_name: str = Field(..., description="Human-readable name")
    source_type: str = Field(..., description="Type of data source")
    connection_config: str = Field(..., description="Connection configuration (JSON string)")
    is_active: bool = Field(..., description="Whether source is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class SourceMappingOut(BaseSchema):
    """Response model for source mapping information"""
    mapping_id: str = Field(..., description="Unique mapping identifier")
    source_id: str = Field(..., description="Data source ID")
    equipment_id: int = Field(..., description="Equipment ID")
    measurement_name: str = Field(..., description="Measurement/table name")
    tag_mappings: str = Field(..., description="Tag mappings (JSON string)")
    field_mappings: str = Field(..., description="Field mappings (JSON string)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class AutoMappingResponse(BaseModel):
    """Response model for auto-mapping operations"""
    message: str = Field(..., description="Result message")
    mappings: List[SourceMappingOut] = Field(default_factory=list, description="Created mappings")
    failed: List[Dict[str, str]] = Field(default_factory=list, description="Failed measurements with reasons")

class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current server time")
    version: Optional[str] = Field(None, description="API version")

# ---------- Error Response Models ----------
class ErrorDetail(BaseModel):
    """Error detail information"""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")

class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = Field(default=False, description="Always false for errors")
    message: str = Field(..., description="Main error message")
    details: List[ErrorDetail] = Field(default_factory=list, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

# ---------- Batch Operation Models ----------
class BatchMappingCreate(BaseModel):
    """Request model for creating multiple mappings"""
    source_id: str = Field(..., description="Data source ID")
    mappings: List[SourceMappingCreate] = Field(..., description="List of mappings to create")

class BatchMappingResponse(BaseModel):
    """Response model for batch mapping operations"""
    total: int = Field(..., description="Total mappings processed")
    created: int = Field(..., description="Successfully created mappings")
    failed: int = Field(..., description="Failed mappings")
    mappings: List[SourceMappingOut] = Field(default_factory=list, description="Created mappings")
    errors: List[ErrorDetail] = Field(default_factory=list, description="Error details for failed mappings")

# ---------- Cache Models ----------
class SchemaCacheInfo(BaseModel):
    """Schema cache information"""
    source_id: str = Field(..., description="Data source ID")
    schema_type: str = Field(..., description="Type of cached schema")
    cached_at: datetime = Field(..., description="Cache creation time")
    expires_at: datetime = Field(..., description="Cache expiration time")
    is_expired: bool = Field(..., description="Whether cache is expired")

class CacheStatusResponse(BaseModel):
    """Response model for cache status"""
    total_entries: int = Field(..., description="Total cache entries")
    expired_entries: int = Field(..., description="Expired cache entries")
    cache_info: List[SchemaCacheInfo] = Field(default_factory=list, description="Detailed cache information")

# ---------- Statistics Models ----------
class SourceStatistics(BaseModel):
    """Statistics for a data source"""
    source_id: str = Field(..., description="Data source ID")
    total_mappings: int = Field(..., description="Total mappings count")
    active_mappings: int = Field(..., description="Active mappings count")
    measurements_count: int = Field(..., description="Available measurements count")
    last_discovery: Optional[datetime] = Field(None, description="Last discovery timestamp")
    connection_status: str = Field(..., description="Current connection status")

class SystemStatistics(BaseModel):
    """Overall system statistics"""
    total_sources: int = Field(..., description="Total data sources")
    active_sources: int = Field(..., description="Active data sources")
    total_mappings: int = Field(..., description="Total mappings")
    source_types: Dict[str, int] = Field(default_factory=dict, description="Count by source type")
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list, description="Recent system activity")

# ---------- Validation Models ----------
class MappingValidation(BaseModel):
    """Mapping validation result"""
    mapping_id: str = Field(..., description="Mapping ID")
    is_valid: bool = Field(..., description="Whether mapping is valid")
    issues: List[str] = Field(default_factory=list, description="Validation issues")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")

class ValidationResponse(BaseModel):
    """Response model for validation operations"""
    total_checked: int = Field(..., description="Total mappings checked")
    valid_mappings: int = Field(..., description="Valid mappings count")
    invalid_mappings: int = Field(..., description="Invalid mappings count")
    results: List[MappingValidation] = Field(default_factory=list, description="Detailed validation results")

# ---------- Export/Import Models ----------
class ExportRequest(BaseModel):
    """Request model for exporting configurations"""
    source_ids: Optional[List[str]] = Field(None, description="Specific source IDs to export")
    include_mappings: bool = Field(default=True, description="Include mappings in export")
    include_config: bool = Field(default=False, description="Include connection configs")
    format: str = Field(default="json", description="Export format")

class ImportRequest(BaseModel):
    """Request model for importing configurations"""
    data: Dict[str, Any] = Field(..., description="Configuration data to import")
    overwrite_existing: bool = Field(default=False, description="Overwrite existing configurations")
    validate_connections: bool = Field(default=True, description="Validate connections during import")

class ImportResponse(BaseModel):
    """Response model for import operations"""
    imported_sources: int = Field(..., description="Successfully imported sources")
    imported_mappings: int = Field(..., description="Successfully imported mappings")
    failed_sources: int = Field(..., description="Failed source imports")
    failed_mappings: int = Field(..., description="Failed mapping imports")
    errors: List[ErrorDetail] = Field(default_factory=list, description="Import errors")
    warnings: List[str] = Field(default_factory=list, description="Import warnings")