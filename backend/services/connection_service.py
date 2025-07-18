# services/connection_service.py - Updated with InfluxDB Support

import sqlite3
import os
import glob
from typing import Dict, Tuple, List
from sqlalchemy.orm import Session
import services.datasource_crud as crud
import pandas as pd
import pyarrow.parquet as pq

# InfluxDB imports (Focus on v2)
try:
    from influxdb_client import InfluxDBClient, QueryApi, BucketsApi
    from influxdb_client.rest import ApiException
    INFLUXDB_AVAILABLE = True
except ImportError:
    INFLUXDB_AVAILABLE = False
    InfluxDBClient = None
    QueryApi = None
    BucketsApi = None
    ApiException = Exception

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
        """Test InfluxDB v2 connection using url, token, org"""
        
        if not INFLUXDB_AVAILABLE:
            return False, "InfluxDB client library not installed. Run: pip install influxdb-client"
        
        try:
            # Extract InfluxDB v2 connection parameters
            url = config.get('url', 'http://localhost:8086')
            token = config.get('token')
            org = config.get('org', 'primary')
            bucket = config.get('bucket')
            
            # Validate required parameters
            if not token:
                return False, "Token is required for InfluxDB v2 connection"
            
            if not bucket:
                return False, "Bucket name is required for InfluxDB v2 connection"
            
            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                return False, "URL must include protocol (http:// or https://)"
            
            try:
                # Create InfluxDB v2 client
                with InfluxDBClient(url=url, token=token, org=org, timeout=10_000) as client:
                    
                    # Test 1: Check if server is ready
                    try:
                        ready = client.ready()
                        if not ready:
                            return False, "InfluxDB v2 server is not ready"
                    except ApiException as e:
                        if e.status == 401:
                            return False, "Authentication failed. Please check your token"
                        elif e.status == 404:
                            return False, f"InfluxDB server not found at {url}"
                        else:
                            return False, f"Server readiness check failed: {str(e)}"
                    
                    # Test 2: Verify organization access
                    try:
                        orgs_api = client.organizations_api()
                        organizations = orgs_api.find_organizations()
                        org_names = [o.name for o in organizations] if organizations else []
                        
                        if org not in org_names:
                            return False, f"Organization '{org}' not found. Available: {org_names[:3]}"
                        
                    except ApiException as e:
                        if e.status == 403:
                            return False, "Insufficient permissions to access organizations"
                        else:
                            return False, f"Organization verification failed: {str(e)}"
                    
                    # Test 3: Verify bucket access
                    try:
                        buckets_api = client.buckets_api()
                        buckets = buckets_api.find_buckets()
                        bucket_names = [b.name for b in buckets.buckets] if buckets.buckets else []
                        
                        if bucket not in bucket_names:
                            # Try to list available buckets for helpful error message
                            available_msg = f"Available buckets: {bucket_names[:5]}" if bucket_names else "No buckets found"
                            return False, f"Bucket '{bucket}' not found in org '{org}'. {available_msg}"
                        
                        # Get bucket details for success message
                        target_bucket = next((b for b in buckets.buckets if b.name == bucket), None)
                        bucket_id = target_bucket.id if target_bucket else "unknown"
                        
                    except ApiException as e:
                        if e.status == 403:
                            return False, "Insufficient permissions to access buckets"
                        else:
                            return False, f"Bucket verification failed: {str(e)}"
                    
                    # Test 4: Test simple query to verify read access
                    try:
                        query_api = client.query_api()
                        
                        # Simple query to test bucket access and get measurement count
                        flux_query = f'''
                        from(bucket: "{bucket}")
                        |> range(start: -1h)
                        |> limit(n: 1)
                        '''
                        
                        # Execute query with timeout
                        result = query_api.query(flux_query)
                        
                        # Count measurements by attempting to get schema
                        schema_query = f'''
                        import "influxdata/influxdb/schema"
                        schema.measurements(bucket: "{bucket}")
                        '''
                        
                        try:
                            measurements_result = query_api.query(schema_query)
                            measurement_count = len(list(measurements_result))
                        except:
                            # If schema query fails, just note data access works
                            measurement_count = "unknown"
                        
                        success_msg = f"InfluxDB v2 connection successful!\n"
                        success_msg += f"✅ Server: {url}\n"
                        success_msg += f"✅ Organization: {org}\n" 
                        success_msg += f"✅ Bucket: {bucket} (ID: {bucket_id[:8]}...)\n"
                        success_msg += f"✅ Measurements: {measurement_count}"
                        
                        return True, success_msg
                        
                    except ApiException as e:
                        if e.status == 403:
                            return False, "Insufficient permissions to query bucket data"
                        else:
                            # Connection works but query failed - still considered success
                            success_msg = f"InfluxDB v2 connection successful (query test failed: {str(e)[:100]})"
                            return True, success_msg
                    except Exception as e:
                        # Connection works but query failed - still considered success
                        success_msg = f"InfluxDB v2 connection successful (bucket accessible, query test skipped)"
                        return True, success_msg
                        
            except ApiException as e:
                if e.status == 401:
                    return False, "Authentication failed. Please verify your token is correct and has necessary permissions"
                elif e.status == 404:
                    return False, f"InfluxDB server not found at {url}. Please check the URL"
                elif e.status == 403:
                    return False, "Access forbidden. Please check token permissions"
                else:
                    return False, f"InfluxDB API error: {str(e)}"
            except Exception as e:
                if "ConnectionError" in str(type(e)):
                    return False, f"Cannot connect to InfluxDB server at {url}. Please check if server is running"
                elif "timeout" in str(e).lower():
                    return False, f"Connection timeout to {url}. Please check network connectivity"
                else:
                    return False, f"InfluxDB connection error: {str(e)}"
            
        except ValueError as e:
            return False, f"Configuration error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected InfluxDB connection error: {str(e)}"
    
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
            
            # Check if it's a directory
            if not os.path.isdir(base_path):
                return False, f"Path is not a directory: {base_path}"
            
            # Look for parquet files
            parquet_files = glob.glob(os.path.join(base_path, "**", "*.parquet"), recursive=True)
            
            if not parquet_files:
                return False, f"No parquet files found in directory: {base_path}"
            
            # Try to read a sample file
            sample_file = parquet_files[0]
            try:
                df = pd.read_parquet(sample_file, engine='pyarrow')
                row_count = len(df)
                col_count = len(df.columns)
                
                return True, f"Parquet connection successful. Found {len(parquet_files)} files. Sample file has {row_count} rows, {col_count} columns"
            except Exception as e:
                return False, f"Cannot read sample parquet file {sample_file}: {str(e)}"
                
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def _discover_parquet_files(base_path: str, limit: int = 1000) -> List[str]:
        """Discover parquet files in the base directory"""
        try:
            pattern = os.path.join(base_path, "**", "*.parquet")
            files = glob.glob(pattern, recursive=True)
            return files[:limit]  # Limit for performance
        except Exception:
            return []
    
    @staticmethod
    def get_parquet_structure_info(config: Dict[str, str]) -> Tuple[bool, Dict, str]:
        """Get structural information about parquet files"""
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