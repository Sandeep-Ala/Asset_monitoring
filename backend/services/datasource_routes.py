# services/datasource_routes.py - Updated with Enhanced Parquet Support

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

import services.datasource_crud as crud
from services.connection_service import test_and_save_connection, ConnectionTestService
from services.schema_discovery_service import get_schema_for_connection, SchemaDiscoveryService
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from config import get_db

datasource_router = InferringRouter()

# ---------- Pydantic Schemas ----------

class DataConnectionCreate(BaseModel):
    name: str
    db_type: str  # sqlite3, influxdb, parquet
    description: Optional[str] = None

class DataConnectionUpdate(BaseModel):
    name: Optional[str] = None
    db_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class DataConnectionOut(BaseModel):
    id: str
    name: str
    db_type: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ConnectionConfigSchema(BaseModel):
    config_key: str
    config_value: str

class ConnectionConfigOut(ConnectionConfigSchema):
    id: int
    connection_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ConnectionTestRequest(BaseModel):
    connection_id: str
    config: Dict[str, str]

class ConnectionTestResponse(BaseModel):
    success: bool
    message: str

class SchemaResponse(BaseModel):
    success: bool
    data: Dict
    message: str

class TablesResponse(BaseModel):
    success: bool
    data: List[Dict]
    message: str

class ColumnsResponse(BaseModel):
    success: bool
    data: List[Dict]
    message: str

# ---------- Routes ----------

@cbv(datasource_router)
class DataSourceRoutes:
    db: Session = Depends(get_db)
    datasource_router.tags = ["Data Sources"]
    datasource_router.prefix = "/datasources"

    # Data Connection Routes
    @datasource_router.post("/connections", response_model=DataConnectionOut)
    def create_connection(self, connection: DataConnectionCreate):
        """Create a new data connection"""
        # Check if connection name already exists
        existing = crud.get_data_connection_by_name(self.db, connection.name)
        if existing:
            raise HTTPException(status_code=400, detail="Connection name already exists")
        
        return crud.create_data_connection(
            self.db, 
            connection.name, 
            connection.db_type, 
            connection.description
        )

    @datasource_router.get("/connections", response_model=List[DataConnectionOut])
    def get_connections(self):
        """Get all data connections"""
        return crud.get_all_data_connections(self.db)

    @datasource_router.get("/connections/{connection_id}", response_model=DataConnectionOut)
    def get_connection(self, connection_id: str):
        """Get data connection by ID"""
        connection = crud.get_data_connection_by_id(self.db, connection_id)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        return connection

    @datasource_router.put("/connections/{connection_id}", response_model=DataConnectionOut)
    def update_connection(self, connection_id: str, update_data: DataConnectionUpdate):
        """Update data connection"""
        connection = crud.update_data_connection(
            self.db, 
            connection_id,
            update_data.name,
            update_data.db_type,
            update_data.description,
            update_data.status
        )
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        return connection

    @datasource_router.delete("/connections/{connection_id}")
    def delete_connection(self, connection_id: str):
        """Delete data connection"""
        connection = crud.delete_data_connection(self.db, connection_id)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        return {"message": "Connection deleted successfully"}

    # Connection Configuration Routes
    @datasource_router.get("/connections/{connection_id}/configs", response_model=List[ConnectionConfigOut])
    def get_connection_configs(self, connection_id: str):
        """Get all configs for a connection"""
        # Verify connection exists
        connection = crud.get_data_connection_by_id(self.db, connection_id)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        return crud.get_connection_configs(self.db, connection_id)

    @datasource_router.get("/connections/{connection_id}/configs/dict")
    def get_connection_configs_dict(self, connection_id: str):
        """Get connection configs as dictionary"""
        # Verify connection exists
        connection = crud.get_data_connection_by_id(self.db, connection_id)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        return crud.get_connection_config_dict(self.db, connection_id)

    @datasource_router.post("/connections/{connection_id}/configs/batch")
    def save_connection_configs(self, connection_id: str, configs: Dict[str, str]):
        """Save multiple connection configs"""
        # Verify connection exists
        connection = crud.get_data_connection_by_id(self.db, connection_id)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        success = crud.save_connection_configs_batch(self.db, connection_id, configs)
        if success:
            return {"message": "Configs saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save configs")

    # Connection Testing Routes
    @datasource_router.post("/connections/test", response_model=ConnectionTestResponse)
    def test_connection(self, test_request: ConnectionTestRequest):
        """Test database connection with provided configuration"""
        success, message = test_and_save_connection(
            self.db, 
            test_request.connection_id, 
            test_request.config
        )
        return ConnectionTestResponse(success=success, message=message)

    @datasource_router.post("/connections/test-only", response_model=ConnectionTestResponse)
    def test_connection_only(self, db_type: str, config: Dict[str, str]):
        """Test connection without saving (for validation during form filling)"""
        success, message = ConnectionTestService.test_connection(db_type, config)
        return ConnectionTestResponse(success=success, message=message)

    # Database Type Information
    @datasource_router.get("/db-types")
    def get_supported_db_types(self):
        """Get list of supported database types and their required config fields"""
        return {
            "sqlite3": {
                "name": "SQLite3",
                "fields": [
                    {"key": "database_path", "label": "Database Path", "type": "text", "required": True, "placeholder": "/path/to/database.db"}
                ]
            },
            "influxdb": {
                "name": "InfluxDB",
                "fields": [
                    {"key": "host", "label": "Host", "type": "text", "required": True, "placeholder": "localhost"},
                    {"key": "port", "label": "Port", "type": "number", "required": True, "placeholder": "8086"},
                    {"key": "database", "label": "Database", "type": "text", "required": True, "placeholder": "mydb"},
                    {"key": "username", "label": "Username", "type": "text", "required": False, "placeholder": "user"},
                    {"key": "password", "label": "Password", "type": "password", "required": False, "placeholder": "password"}
                ]
            },
            "parquet": {
                "name": "Parquet Files",
                "description": "Time-series data stored in partitioned Parquet files",
                "fields": [
                    {
                        "key": "base_path", 
                        "label": "Base Directory Path", 
                        "type": "text", 
                        "required": True, 
                        "placeholder": "D:\\Data-Backup\\site=UK_Tollgate",
                        "help": "Path to the root directory containing partitioned parquet files (e.g., site=*/year=*/month=*/day=*/equipment=*/dcu=*/*.parquet)"
                    }
                ]
            }
        }

    # Schema Discovery Routes
    @datasource_router.get("/connections/{connection_id}/tables", response_model=TablesResponse)
    def get_connection_tables(self, connection_id: str):
        """Get all tables for a connection"""
        success, data, message = get_schema_for_connection(self.db, connection_id)
        return TablesResponse(success=success, data=data, message=message)

    @datasource_router.get("/connections/{connection_id}/tables/{table_name}/columns", response_model=ColumnsResponse)
    def get_table_columns(self, connection_id: str, table_name: str):
        """Get columns for a specific table"""
        success, data, message = get_schema_for_connection(self.db, connection_id, table_name)
        return ColumnsResponse(success=success, data=data, message=message)

    @datasource_router.get("/connections/{connection_id}/schema", response_model=SchemaResponse)
    def get_complete_schema(self, connection_id: str, quick_mode: bool = True):
        """Get complete schema information for a connection"""
        # Get connection
        connection = crud.get_data_connection_by_id(self.db, connection_id)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        if connection.status != "active":
            return SchemaResponse(success=False, data={}, message="Connection is not active")
        
        # Get connection config
        config = crud.get_connection_config_dict(self.db, connection_id)
        if not config:
            return SchemaResponse(success=False, data={}, message="Connection configuration not found")
        
        # Add db_type to config for schema discovery
        config['db_type'] = connection.db_type
        
        # Get complete schema based on database type
        if connection.db_type.lower() == "sqlite3":
            success, data, message = SchemaDiscoveryService.get_complete_schema(config, quick_mode)
        elif connection.db_type.lower() == "parquet":
            success, data, message = SchemaDiscoveryService.get_complete_schema(config, quick_mode)
        elif connection.db_type.lower() == "influxdb":
            success, data, message = False, {}, f"InfluxDB schema discovery not yet implemented"
        else:
            success, data, message = False, {}, f"Schema discovery not implemented for {connection.db_type}"
        
        return SchemaResponse(success=success, data=data, message=message)

    @datasource_router.get("/connections/{connection_id}/quick-info")
    def get_connection_quick_info(self, connection_id: str):
        """Get quick connection information for UI display"""
        connection = crud.get_data_connection_by_id(self.db, connection_id)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        config = crud.get_connection_config_dict(self.db, connection_id)
        
        result = {
            "connection": {
                "id": connection.id,
                "name": connection.name,
                "db_type": connection.db_type,
                "status": connection.status,
                "description": connection.description
            },
            "config": config
        }
        
        # Add quick stats if connection is active
        if connection.status == "active" and config:
            if connection.db_type.lower() == "sqlite3":
                success, tables, _ = SchemaDiscoveryService.get_sqlite_tables(config)
                if success:
                    result["stats"] = {
                        "total_tables": len(tables),
                        "table_names": [t["name"] for t in tables[:10]]  # First 10 table names
                    }
            elif connection.db_type.lower() == "parquet":
                config['db_type'] = connection.db_type  # Add db_type for parquet
                success, tables, _ = SchemaDiscoveryService.get_parquet_tables(config)
                if success:
                    result["stats"] = {
                        "total_tables": len(tables),
                        "equipment_types": [t["name"] for t in tables[:10]],  # First 10 equipment types
                        "base_path": config.get('base_path')
                    }
        
        return result

    # Additional Parquet-specific route for structure analysis
    @datasource_router.get("/connections/{connection_id}/parquet-structure")
    def get_parquet_structure_info(self, connection_id: str):
        """Get detailed Parquet directory structure information"""
        connection = crud.get_data_connection_by_id(self.db, connection_id)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        if connection.db_type.lower() != "parquet":
            raise HTTPException(status_code=400, detail="This endpoint is only for Parquet connections")
        
        config = crud.get_connection_config_dict(self.db, connection_id)
        if not config:
            raise HTTPException(status_code=404, detail="Connection configuration not found")
        
        # Get detailed structure information
        success, structure_info, message = ConnectionTestService.get_parquet_structure_info(config)
        
        if success:
            return {
                "success": True,
                "data": structure_info,
                "message": message
            }
        else:
            return {
                "success": False,
                "data": {},
                "message": message
            }

# Router export
router = datasource_router