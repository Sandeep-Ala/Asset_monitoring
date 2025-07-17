# services/connection_service.py - Updated with Parquet Support

import sqlite3
import os
import glob
from typing import Dict, Tuple, List
from sqlalchemy.orm import Session
import services.datasource_crud as crud
import pandas as pd
import pyarrow.parquet as pq
class ConnectionTestService:
    """Service to test different database connections"""
    
    @staticmethod
    def test_sqlite_connection(config: Dict[str, str]) -> Tuple[bool, str]:
        """Test SQLite3 connection"""
        try:
            db_path = config.get('database_path')
            if not db_path:
                return False, "Database path is required for SQLite connection"
            
            # Check if file exists
            if not os.path.exists(db_path):
                return False, f"Database file not found at path: {db_path}"
            
            # Try to connect
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Test with a simple query
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;")
            result = cursor.fetchone()
            
            conn.close()
            
            return True, "SQLite connection successful"
            
        except sqlite3.Error as e:
            return False, f"SQLite connection failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def test_influxdb_connection(config: Dict[str, str]) -> Tuple[bool, str]:
        """Test InfluxDB connection (placeholder for future implementation)"""
        # TODO: Implement InfluxDB connection testing
        return False, "InfluxDB connection testing not yet implemented"
    
    @staticmethod
    def test_parquet_connection(config: Dict[str, str]) -> Tuple[bool, str]:
        """Test Parquet files connection"""
        try:
            base_path = config.get('base_path')
            if not base_path:
                return False, "Base path is required for Parquet connection"
            
            # Check if directory exists
            if not os.path.exists(base_path):
                return False, f"Directory not found at path: {base_path}"
            
            if not os.path.isdir(base_path):
                return False, f"Path is not a directory: {base_path}"
            
            # Try to find parquet files with the expected structure
            parquet_files = ConnectionTestService._discover_parquet_files(base_path)
            
            if not parquet_files:
                return False, "No parquet files found in the specified directory structure"
            
            # Try to read schema from one file to validate it's a valid parquet
            try:
                
                sample_file = parquet_files[0]
                
                # Use pyarrow to read just the schema first (faster)
                try:
                    parquet_file = pq.ParquetFile(sample_file)
                    schema = parquet_file.schema_arrow
                    column_count = len(schema)
                    
                    return True, f"Parquet connection successful. Found {len(parquet_files)} parquet files with {column_count} columns in sample file."
                    
                except Exception:
                    # Fallback to pandas without nrows parameter
                    df_sample = pd.read_parquet(sample_file)
                    if len(df_sample) > 0:
                        df_sample = df_sample.head(1)  # Take just first row
                    
                    return True, f"Parquet connection successful. Found {len(parquet_files)} parquet files with {len(df_sample.columns)} columns in sample file."
                
            except Exception as e:
                return False, f"Failed to read parquet file: {str(e)}"
            
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def _discover_parquet_files(base_path: str, limit: int = 100) -> List[str]:
        """Discover parquet files in the directory structure"""
        parquet_files = []
        
        try:
            # Search pattern for parquet files in partitioned structure
            # Pattern: base_path/**/equipment=*/dcu=*/*.parquet
            search_pattern = os.path.join(base_path, "**", "equipment=*", "dcu=*", "*.parquet")
            
            # Use glob to find all matching files
            found_files = glob.glob(search_pattern, recursive=True)
            
            # Limit results for performance during connection testing
            parquet_files = found_files[:limit]
            
            return parquet_files
            
        except Exception as e:
            print(f"Error discovering parquet files: {str(e)}")
            return []
    
    @staticmethod
    def get_parquet_structure_info(config: Dict[str, str]) -> Tuple[bool, Dict, str]:
        """Get basic structure information about parquet files"""
        try:
            base_path = config.get('base_path')
            if not base_path or not os.path.exists(base_path):
                return False, {}, "Invalid base path"
            
            # Discover all parquet files
            all_files = ConnectionTestService._discover_parquet_files(base_path, limit=1000)
            
            if not all_files:
                return False, {}, "No parquet files found"
            
            # Extract unique equipment types and dcu values
            equipment_types = set()
            dcu_values = set()
            
            for file_path in all_files:
                # Extract equipment and dcu from path
                path_parts = file_path.replace(base_path, "").split(os.sep)
                
                for part in path_parts:
                    if part.startswith("equipment="):
                        equipment_types.add(part.split("=")[1])
                    elif part.startswith("dcu="):
                        dcu_values.add(part.split("=")[1])
            
            structure_info = {
                "total_files": len(all_files),
                "equipment_types": sorted(list(equipment_types)),
                "dcu_values": sorted(list(dcu_values)),
                "base_path": base_path,
                "sample_files": all_files[:5]  # First 5 files as samples
            }
            
            return True, structure_info, "Structure analysis completed"
            
        except Exception as e:
            return False, {}, f"Error analyzing structure: {str(e)}"
    
    @staticmethod
    def test_connection(db_type: str, config: Dict[str, str]) -> Tuple[bool, str]:
        """Test connection based on database type"""
        if db_type.lower() == 'sqlite3':
            return ConnectionTestService.test_sqlite_connection(config)
        elif db_type.lower() == 'influxdb':
            return ConnectionTestService.test_influxdb_connection(config)
        elif db_type.lower() == 'parquet':
            return ConnectionTestService.test_parquet_connection(config)
        else:
            return False, f"Unsupported database type: {db_type}"

def test_and_save_connection(db: Session, connection_id: str, config: Dict[str, str]) -> Tuple[bool, str]:
    """Test connection and update status in database"""
    connection = crud.get_data_connection_by_id(db, connection_id)
    if not connection:
        return False, "Connection not found"
    
    # Test the connection
    is_success, message = ConnectionTestService.test_connection(connection.db_type, config)
    
    # Update connection status
    new_status = "active" if is_success else "error"
    crud.update_data_connection(db, connection_id, status=new_status)
    
    # Save configuration if test is successful
    if is_success:
        crud.save_connection_configs_batch(db, connection_id, config)
    
    return is_success, message