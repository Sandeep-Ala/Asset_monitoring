# backend/services/discovery_services.py
import requests
import duckdb
import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import pandas as pd
from io import StringIO
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """InfluxDB discovery implementation using both REST API and Flux queries"""
    
    def __init__(self, connection_config: dict):
        super().__init__(connection_config)
        self.url = connection_config.get('url', '').rstrip('/')
        self.token = connection_config.get('token', '')
        self.org = connection_config.get('org', '')
        self.bucket = connection_config.get('bucket', '')
        
        # Headers for different API endpoints
        self.flux_headers = {
            'Authorization': f'Token {self.token}',
            'Accept': 'application/csv',
            'Content-Type': 'application/vnd.flux'
        }
        
        self.rest_headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
        
        self.timeout = 30
        self.max_retries = 3
    
    def test_connection(self) -> Dict[str, Any]:
        """Test InfluxDB connection using multiple validation methods"""
        try:
            logger.info(f"Testing InfluxDB connection to {self.url}")
            
            # 1. Health check
            health_url = f"{self.url}/health"
            health_response = requests.get(health_url, timeout=10)
            
            if health_response.status_code != 200:
                return {
                    "success": False,
                    "message": f"InfluxDB health check failed: {health_response.status_code}",
                    "details": {"response": health_response.text[:500]}
                }
            
            # 2. Test authentication and org access
            ping_url = f"{self.url}/api/v2/ping"
            ping_response = requests.get(ping_url, headers=self.rest_headers, timeout=10)
            
            if ping_response.status_code != 204:
                return {
                    "success": False,
                    "message": f"Authentication failed: {ping_response.status_code}",
                    "details": {"response": ping_response.text[:500]}
                }
            
            # 3. Test bucket access using REST API
            buckets_url = f"{self.url}/api/v2/buckets"
            params = {"org": self.org, "name": self.bucket}
            buckets_response = requests.get(
                buckets_url, 
                headers=self.rest_headers, 
                params=params,
                timeout=10
            )
            
            bucket_accessible = False
            if buckets_response.status_code == 200:
                buckets_data = buckets_response.json()
                bucket_accessible = len(buckets_data.get('buckets', [])) > 0
            
            # 4. Test query capability with simple Flux query
            simple_query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -1h)
            |> limit(n: 1)
            '''
            
            query_result = self._execute_flux_query(simple_query)
            query_accessible = query_result is not None
            
            success = bucket_accessible and query_accessible
            
            return {
                "success": success,
                "message": "Connection successful" if success else "Partial connection issues",
                "details": {
                    "url": self.url,
                    "org": self.org,
                    "bucket": self.bucket,
                    "health_check": health_response.status_code == 200,
                    "authentication": ping_response.status_code == 204,
                    "bucket_access": bucket_accessible,
                    "query_access": query_accessible
                }
            }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "Connection timeout - InfluxDB server not responding",
                "details": {"error": "timeout"}
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "Cannot connect to InfluxDB server - check URL and network",
                "details": {"error": "connection_error"}
            }
        except Exception as e:
            logger.error(f"InfluxDB connection test failed: {e}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def discover_measurements(self) -> List[str]:
        """Get list of measurements from InfluxDB using multiple methods"""
        try:
            logger.info(f"Discovering measurements for bucket: {self.bucket}")
            
            # Method 1: Try Flux query with schema.measurements()
            measurements = self._discover_measurements_flux()
            if measurements:
                logger.info(f"Found {len(measurements)} measurements via Flux")
                return measurements
            
            # Method 2: Try REST API approach (fallback)
            measurements = self._discover_measurements_rest()
            if measurements:
                logger.info(f"Found {len(measurements)} measurements via REST API")
                return measurements
            
            # Method 3: Try sampling approach (last resort)
            measurements = self._discover_measurements_sampling()
            logger.info(f"Found {len(measurements)} measurements via sampling")
            return measurements
            
        except Exception as e:
            logger.error(f"Error discovering measurements: {e}")
            return []
    
    def _discover_measurements_flux(self) -> List[str]:
        """Discover measurements using Flux schema functions"""
        try:
            query = f'''
            import "influxdata/influxdb/schema"
            schema.measurements(bucket: "{self.bucket}")
            '''
            
            response = self._execute_flux_query(query)
            if response:
                df = pd.read_csv(StringIO(response))
                if '_value' in df.columns:
                    measurements = df['_value'].dropna().unique().tolist()
                    return [str(m) for m in measurements if str(m) != 'nan']
            return []
            
        except Exception as e:
            logger.warning(f"Flux measurements discovery failed: {e}")
            return []
    
    def _discover_measurements_rest(self) -> List[str]:
        """Discover measurements using REST API query approach"""
        try:
            # Use a broader query to find measurements
            query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -7d)
            |> group(columns: ["_measurement"])
            |> distinct(column: "_measurement")
            |> keep(columns: ["_measurement"])
            '''
            
            response = self._execute_flux_query(query)
            if response:
                df = pd.read_csv(StringIO(response))
                if '_measurement' in df.columns:
                    measurements = df['_measurement'].dropna().unique().tolist()
                    return [str(m) for m in measurements if str(m) != 'nan']
            return []
            
        except Exception as e:
            logger.warning(f"REST measurements discovery failed: {e}")
            return []
    
    def _discover_measurements_sampling(self) -> List[str]:
        """Discover measurements by sampling recent data"""
        try:
            query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -24h)
            |> limit(n: 100)
            |> keep(columns: ["_measurement"])
            |> distinct(column: "_measurement")
            '''
            
            response = self._execute_flux_query(query)
            if response:
                df = pd.read_csv(StringIO(response))
                if '_measurement' in df.columns:
                    measurements = df['_measurement'].dropna().unique().tolist()
                    return [str(m) for m in measurements if str(m) != 'nan']
            return []
            
        except Exception as e:
            logger.warning(f"Sampling measurements discovery failed: {e}")
            return []
    
    def discover_tags(self, measurement: str) -> List[str]:
        """Get tag keys for a measurement using multiple methods"""
        try:
            logger.info(f"Discovering tags for measurement: {measurement}")
            
            # Method 1: Flux schema.tagKeys()
            tags = self._discover_tags_flux(measurement)
            if tags:
                return tags
            
            # Method 2: Sample data approach
            tags = self._discover_tags_sampling(measurement)
            return tags
            
        except Exception as e:
            logger.error(f"Error discovering tags for {measurement}: {e}")
            return []
    
    def _discover_tags_flux(self, measurement: str) -> List[str]:
        """Discover tags using Flux schema functions"""
        try:
            query = f'''
            import "influxdata/influxdb/schema"
            schema.tagKeys(
                bucket: "{self.bucket}",
                predicate: (r) => r._measurement == "{measurement}"
            )
            '''
            
            response = self._execute_flux_query(query)
            if response:
                df = pd.read_csv(StringIO(response))
                if '_value' in df.columns:
                    tags = df['_value'].dropna().unique().tolist()
                    return [str(t) for t in tags if str(t) != 'nan']
            return []
            
        except Exception as e:
            logger.warning(f"Flux tags discovery failed for {measurement}: {e}")
            return []
    
    def _discover_tags_sampling(self, measurement: str) -> List[str]:
        """Discover tags by sampling measurement data"""
        try:
            query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -24h)
            |> filter(fn: (r) => r._measurement == "{measurement}")
            |> limit(n: 10)
            '''
            
            response = self._execute_flux_query(query)
            if response:
                df = pd.read_csv(StringIO(response))
                # Get all columns that are not standard InfluxDB columns
                standard_cols = {'_time', '_measurement', '_field', '_value', '_start', '_stop', 'table', 'result'}
                tag_cols = [col for col in df.columns if col not in standard_cols]
                return tag_cols
            return []
            
        except Exception as e:
            logger.warning(f"Sampling tags discovery failed for {measurement}: {e}")
            return []
    
    def discover_fields(self, measurement: str) -> List[Dict[str, str]]:
        """Get field keys and types for a measurement"""
        try:
            logger.info(f"Discovering fields for measurement: {measurement}")
            
            # Method 1: Flux schema.fieldKeys()
            fields = self._discover_fields_flux(measurement)
            if fields:
                return fields
            
            # Method 2: Sample data approach
            fields = self._discover_fields_sampling(measurement)
            return fields
            
        except Exception as e:
            logger.error(f"Error discovering fields for {measurement}: {e}")
            return []
    
    def _discover_fields_flux(self, measurement: str) -> List[Dict[str, str]]:
        """Discover fields using Flux schema functions"""
        try:
            query = f'''
            import "influxdata/influxdb/schema"
            schema.fieldKeys(
                bucket: "{self.bucket}",
                predicate: (r) => r._measurement == "{measurement}"
            )
            '''
            
            response = self._execute_flux_query(query)
            if response:
                df = pd.read_csv(StringIO(response))
                if '_value' in df.columns:
                    fields = df['_value'].dropna().unique().tolist()
                    # For now, assume all fields are float - could be enhanced
                    return [{"name": str(f), "type": "float"} for f in fields if str(f) != 'nan']
            return []
            
        except Exception as e:
            logger.warning(f"Flux fields discovery failed for {measurement}: {e}")
            return []
    
    def _discover_fields_sampling(self, measurement: str) -> List[Dict[str, str]]:
        """Discover fields by sampling measurement data"""
        try:
            query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -24h)
            |> filter(fn: (r) => r._measurement == "{measurement}")
            |> limit(n: 10)
            '''
            
            response = self._execute_flux_query(query)
            if response:
                df = pd.read_csv(StringIO(response))
                if '_field' in df.columns:
                    fields = df['_field'].dropna().unique().tolist()
                    return [{"name": str(f), "type": "float"} for f in fields if str(f) != 'nan']
            return []
            
        except Exception as e:
            logger.warning(f"Sampling fields discovery failed for {measurement}: {e}")
            return []
    
    def get_sample_data(self, measurement: str, limit: int = 10) -> List[Dict]:
        """Get sample data from measurement"""
        try:
            logger.info(f"Getting sample data for measurement: {measurement}")
            
            query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -24h)
            |> filter(fn: (r) => r._measurement == "{measurement}")
            |> limit(n: {limit})
            '''
            
            response = self._execute_flux_query(query)
            if response:
                df = pd.read_csv(StringIO(response))
                return df.to_dict('records')
            return []
            
        except Exception as e:
            logger.error(f"Error getting sample data for {measurement}: {e}")
            return []
    
    def _execute_flux_query(self, query: str) -> Optional[str]:
        """Execute Flux query with retry logic and return CSV response"""
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Executing Flux query (attempt {attempt + 1}): {query[:100]}...")
                
                query_url = f"{self.url}/api/v2/query?org={self.org}"
                response = requests.post(
                    query_url,
                    headers=self.flux_headers,
                    data=query,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    content = response.text.strip()
                    if content and not content.startswith('{"error"'):
                        return content
                    else:
                        logger.warning(f"Empty or error response: {content[:200]}")
                        return None
                        
                elif response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                    continue
                    
                else:
                    logger.error(f"Query failed: {response.status_code} - {response.text[:500]}")
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Query timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                return None
                
            except Exception as e:
                logger.error(f"Query execution error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                return None
        
        logger.error(f"Query failed after {self.max_retries} attempts")
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
            logger.info(f"Testing Parquet connection to {self.base_path}")
            
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
                # Test reading capability
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
            logger.error(f"Parquet connection test failed: {e}")
            return {
                "success": False,
                "message": f"Connection test failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def discover_measurements(self) -> List[str]:
        """Discover unique equipment types from parquet structure"""
        try:
            logger.info(f"Discovering measurements from {self.base_path}")
            
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
            
            measurements = list(equipments)
            logger.info(f"Found {len(measurements)} equipment types")
            return measurements
            
        except Exception as e:
            logger.error(f"Error discovering measurements: {e}")
            return []
    
    def discover_tags(self, measurement: str) -> List[str]:
        """Get tag columns from parquet files"""
        try:
            logger.info(f"Discovering tags for equipment: {measurement}")
            
            # Build path pattern for specific equipment
            equipment_pattern = os.path.join(self.base_path, f"**/equipment={measurement}/**/*.parquet")
            
            con = duckdb.connect(':memory:')
            
            try:
                # Get column names
                result = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{equipment_pattern}') LIMIT 1").fetchall()
                
                # Filter columns that look like tags (typically n_*, id columns, etc.)
                tag_columns = []
                for row in result:
                    column_name = row[0]
                    # Common tag patterns
                    if (column_name.startswith('n_') and 
                        not column_name.startswith('n_soc') and 
                        not column_name.startswith('n_voltage') and
                        not column_name.startswith('n_current')):
                        tag_columns.append(column_name)
                
                logger.info(f"Found {len(tag_columns)} tag columns")
                return tag_columns
                
            finally:
                con.close()
            
        except Exception as e:
            logger.error(f"Error discovering tags for {measurement}: {e}")
            return []
    
    def discover_fields(self, measurement: str) -> List[Dict[str, str]]:
        """Get field columns and types from parquet files"""
        try:
            logger.info(f"Discovering fields for equipment: {measurement}")
            
            # Build path pattern for specific equipment
            equipment_pattern = os.path.join(self.base_path, f"**/equipment={measurement}/**/*.parquet")
            
            con = duckdb.connect(':memory:')
            
            try:
                # Get column names and types
                result = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{equipment_pattern}') LIMIT 1").fetchall()
                
                # Filter columns that look like fields (typically measurement values)
                field_columns = []
                for row in result:
                    column_name, column_type = row[0], row[1]
                    # Common field patterns - numeric measurements
                    if (column_name.startswith(('n_soc', 'n_voltage', 'n_current', 'n_temperature', 'n_power')) or
                        column_name in ['value', 'measurement', 'reading']):
                        field_columns.append({
                            "name": column_name,
                            "type": column_type.lower()
                        })
                
                logger.info(f"Found {len(field_columns)} field columns")
                return field_columns
                
            finally:
                con.close()
            
        except Exception as e:
            logger.error(f"Error discovering fields for {measurement}: {e}")
            return []
    
    def get_sample_data(self, measurement: str, limit: int = 10) -> List[Dict]:
        """Get sample data from parquet files"""
        try:
            logger.info(f"Getting sample data for equipment: {measurement}")
            
            # Build path pattern for specific equipment
            equipment_pattern = os.path.join(self.base_path, f"**/equipment={measurement}/**/*.parquet")
            
            con = duckdb.connect(':memory:')
            
            try:
                # Get sample data
                result = con.execute(f"SELECT * FROM read_parquet('{equipment_pattern}') LIMIT {limit}").fetchdf()
                
                return result.to_dict('records')
                
            finally:
                con.close()
            
        except Exception as e:
            logger.error(f"Error getting sample data for {measurement}: {e}")
            return []

# Factory function to get appropriate discovery service
def get_discovery_service(source_type: str, connection_config: dict) -> DataSourceDiscovery:
    """Factory function to get appropriate discovery service"""
    if source_type.lower() == 'influxdb':
        return InfluxDBDiscovery(connection_config)
    elif source_type.lower() == 'parquet':
        return ParquetDiscovery(connection_config)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")