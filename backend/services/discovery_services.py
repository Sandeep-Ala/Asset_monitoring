# backend/services/discovery_services.py
import requests
import duckdb
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd

class DataSourceDiscovery:
    """Base class for data source discovery"""
    
    def __init__(self, connection_config: dict):
        self.connection_config = connection_config
    
    def test_connection(self) -> Dict[str, Any]:
        """Test if connection is working"""
        raise NotImplementedError
    
    def discover_measurements(self) -> List[str]:
        """Get list of measurements/tables"""
        raise NotImplementedError
    
    def discover_tags(self, measurement: str) -> List[str]:
        """Get list of tag keys for a measurement"""
        raise NotImplementedError
    
    def discover_fields(self, measurement: str) -> List[Dict[str, str]]:
        """Get list of field keys and types for a measurement"""
        raise NotImplementedError
    
    def get_sample_data(self, measurement: str, limit: int = 10) -> List[Dict]:
        """Get sample data from measurement"""
        raise NotImplementedError

class InfluxDBDiscovery(DataSourceDiscovery):
    """InfluxDB discovery implementation"""
    
    def __init__(self, connection_config: dict):
        super().__init__(connection_config)
        self.url = connection_config.get('url', '')
        self.token = connection_config.get('token', '')
        self.org = connection_config.get('org', '')
        self.bucket = connection_config.get('bucket', '')
        
        self.headers = {
            'Authorization': f'Token {self.token}',
            'Accept': 'application/csv',
            'Content-Type': 'application/vnd.flux'
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test InfluxDB connection"""
        try:
            # Simple health check
            health_url = f"{self.url}/health"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                # Test query access
                query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -1h)
                |> limit(n: 1)
                '''
                
                query_url = f"{self.url}/api/v2/query?org={self.org}"
                query_response = requests.post(
                    query_url, 
                    headers=self.headers,
                    data=query,
                    timeout=15
                )
                
                return {
                    "success": True,
                    "message": "Connection successful",
                    "details": {
                        "url": self.url,
                        "org": self.org,
                        "bucket": self.bucket,
                        "query_access": query_response.status_code == 200
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"Health check failed: {response.status_code}",
                    "details": {"response": response.text}
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def discover_measurements(self) -> List[str]:
        """Get list of measurements from InfluxDB"""
        try:
            query = f'''
            import "influxdata/influxdb/schema"
            schema.measurements(bucket: "{self.bucket}")
            '''
            
            response = self._execute_query(query)
            if response:
                # Parse CSV response to get measurement names
                df = pd.read_csv(pd.StringIO(response))
                return df['_value'].tolist() if '_value' in df.columns else []
            return []
            
        except Exception as e:
            print(f"Error discovering measurements: {e}")
            return []
    
    def discover_tags(self, measurement: str) -> List[str]:
        """Get tag keys for a measurement"""
        try:
            query = f'''
            import "influxdata/influxdb/schema"
            schema.tagKeys(
                bucket: "{self.bucket}",
                predicate: (r) => r._measurement == "{measurement}"
            )
            '''
            
            response = self._execute_query(query)
            if response:
                df = pd.read_csv(pd.StringIO(response))
                return df['_value'].tolist() if '_value' in df.columns else []
            return []
            
        except Exception as e:
            print(f"Error discovering tags: {e}")
            return []
    
    def discover_fields(self, measurement: str) -> List[Dict[str, str]]:
        """Get field keys and types for a measurement"""
        try:
            query = f'''
            import "influxdata/influxdb/schema"
            schema.fieldKeys(
                bucket: "{self.bucket}",
                predicate: (r) => r._measurement == "{measurement}"
            )
            '''
            
            response = self._execute_query(query)
            if response:
                df = pd.read_csv(pd.StringIO(response))
                return [{"name": field, "type": "float"} for field in df['_value'].tolist()]
            return []
            
        except Exception as e:
            print(f"Error discovering fields: {e}")
            return []
    
    def get_sample_data(self, measurement: str, limit: int = 10) -> List[Dict]:
        """Get sample data from measurement"""
        try:
            query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -24h)
            |> filter(fn: (r) => r._measurement == "{measurement}")
            |> limit(n: {limit})
            '''
            
            response = self._execute_query(query)
            if response:
                df = pd.read_csv(pd.StringIO(response))
                return df.to_dict('records')
            return []
            
        except Exception as e:
            print(f"Error getting sample data: {e}")
            return []
    
    def _execute_query(self, query: str) -> Optional[str]:
        """Execute Flux query and return CSV response"""
        try:
            query_url = f"{self.url}/api/v2/query?org={self.org}"
            response = requests.post(
                query_url,
                headers=self.headers,
                data=query,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"Query failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Query execution error: {e}")
            return None

class ParquetDiscovery(DataSourceDiscovery):
    """Parquet discovery implementation using DuckDB"""
    
    def __init__(self, connection_config: dict):
        super().__init__(connection_config)
        self.base_path = connection_config.get('base_path', '')
        self.path_pattern = connection_config.get('path_pattern', '**/*.parquet')
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Parquet path access"""
        try:
            if not os.path.exists(self.base_path):
                return {
                    "success": False,
                    "message": f"Path does not exist: {self.base_path}",
                    "details": {"base_path": self.base_path}
                }
            
            # Try to list some parquet files
            full_pattern = os.path.join(self.base_path, self.path_pattern)
            con = duckdb.connect(':memory:')
            
            try:
                result = con.execute(f"SELECT COUNT(*) FROM read_parquet('{full_pattern}') LIMIT 1").fetchone()
                file_count = result[0] if result else 0
                
                return {
                    "success": True,
                    "message": "Connection successful",
                    "details": {
                        "base_path": self.base_path,
                        "pattern": self.path_pattern,
                        "accessible_records": file_count
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Cannot read parquet files: {str(e)}",
                    "details": {"error": str(e)}
                }
            finally:
                con.close()
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection test failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def discover_measurements(self) -> List[str]:
        """Discover unique equipment types from parquet structure"""
        try:
            # Extract equipment types from directory structure
            equipments = set()
            
            for root, dirs, files in os.walk(self.base_path):
                for file in files:
                    if file.endswith('.parquet'):
                        rel_path = os.path.relpath(root, self.base_path)
                        path_parts = rel_path.split(os.sep)
                        
                        # Look for equipment= pattern
                        for part in path_parts:
                            if part.startswith('equipment='):
                                equipment = part.split('=')[1]
                                equipments.add(equipment)
            
            return list(equipments)
            
        except Exception as e:
            print(f"Error discovering measurements: {e}")
            return []
    
    def discover_tags(self, measurement: str) -> List[str]:
        """Get tag columns from parquet files"""
        try:
            # Build path pattern for specific equipment
            equipment_pattern = self.base_path.replace('*', measurement)
            pattern = os.path.join(equipment_pattern, "*.parquet")
            
            con = duckdb.connect(':memory:')
            
            try:
                # Get column names
                result = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{pattern}') LIMIT 1").fetchall()
                
                # Filter columns that look like tags (typically n_*, id columns, etc.)
                tag_columns = []
                for row in result:
                    col_name = row[0]
                    if (col_name.startswith('n_') or 
                        col_name.endswith('_id') or 
                        col_name in ['rack', 'bank', 'module', 'cell']):
                        tag_columns.append(col_name)
                
                return tag_columns
                
            finally:
                con.close()
                
        except Exception as e:
            print(f"Error discovering tags: {e}")
            return []
    
    def discover_fields(self, measurement: str) -> List[Dict[str, str]]:
        """Get field columns and types from parquet files"""
        try:
            # Build path pattern for specific equipment
            equipment_pattern = self.base_path.replace('*', measurement)
            pattern = os.path.join(equipment_pattern, "*.parquet")
            
            con = duckdb.connect(':memory:')
            
            try:
                # Get column info
                result = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{pattern}') LIMIT 1").fetchall()
                
                # Filter numeric columns that look like fields
                field_columns = []
                for row in result:
                    col_name, col_type = row[0], row[1]
                    if (col_type in ['DOUBLE', 'FLOAT', 'INTEGER', 'BIGINT'] and 
                        not col_name.startswith('n_') and 
                        col_name != 't_sampling_time'):
                        field_columns.append({
                            "name": col_name,
                            "type": col_type.lower()
                        })
                
                return field_columns
                
            finally:
                con.close()
                
        except Exception as e:
            print(f"Error discovering fields: {e}")
            return []
    
    def get_sample_data(self, measurement: str, limit: int = 10) -> List[Dict]:
        """Get sample data from parquet files"""
        try:
            # Build path pattern for specific equipment
            equipment_pattern = self.base_path.replace('*', measurement)
            pattern = os.path.join(equipment_pattern, "*.parquet")
            
            con = duckdb.connect(':memory:')
            
            try:
                result = con.execute(f"SELECT * FROM read_parquet('{pattern}') LIMIT {limit}").fetchdf()
                return result.to_dict('records')
                
            finally:
                con.close()
                
        except Exception as e:
            print(f"Error getting sample data: {e}")
            return []

def get_discovery_service(source_type: str, connection_config: dict) -> DataSourceDiscovery:
    """Factory function to get appropriate discovery service"""
    if source_type.lower() == 'influxdb':
        return InfluxDBDiscovery(connection_config)
    elif source_type.lower() == 'parquet':
        return ParquetDiscovery(connection_config)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")