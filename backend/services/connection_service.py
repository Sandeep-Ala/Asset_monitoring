# services/connection_service.py

import sqlite3
import os
from typing import Dict, Tuple
from sqlalchemy.orm import Session
import services.datasource_crud as crud

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
        """Test Parquet files connection (placeholder for future implementation)"""
        # TODO: Implement Parquet connection testing
        return False, "Parquet connection testing not yet implemented"
    
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