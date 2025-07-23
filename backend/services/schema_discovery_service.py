# services/schema_discovery_service.py - COMBINED InfluxDB + Parquet + SQLite Implementation
# Complete schema discovery service supporting all three data source types

import sqlite3
import os
import glob
import pandas as pd
from typing import List, Dict, Tuple, Optional, Set
from sqlalchemy.orm import Session
import services.datasource_crud as crud
from collections import defaultdict
import pyarrow.parquet as pq
import requests
import json

# InfluxDB v2 imports (with fallback handling)
try:
    from influxdb_client import InfluxDBClient, QueryApi
    from influxdb_client.rest import ApiException
    INFLUXDB_AVAILABLE = True
    print("✅ InfluxDB client library available")
except ImportError:
    INFLUXDB_AVAILABLE = False
    InfluxDBClient = None
    QueryApi = None
    ApiException = Exception
    print("⚠️ InfluxDB client library not installed")

class SchemaDiscoveryService:
    """
    Service to discover database schema for different database types
    
    COMBINED IMPLEMENTATION:
    - InfluxDB v2 REST API with comprehensive measurement/field/tag discovery
    - Optimized Parquet analysis with partition and column detection
    - SQLite schema discovery with performance optimizations
    - Cross-platform compatibility and robust error handling
    """
    
    # =================== SQLITE METHODS (Enhanced from both implementations) ===================
    
    @staticmethod
    def get_sqlite_tables(config: Dict[str, str]) -> Tuple[bool, List[Dict], str]:
        """Get all tables from SQLite database with optimized queries"""
        try:
            db_path = config.get('database_path')
            if not db_path or not os.path.exists(db_path):
                return False, [], "Database file not found"
            
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA journal_mode = WAL")  # Performance optimization
            conn.execute("PRAGMA synchronous = NORMAL")  # Performance optimization
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("""
                SELECT name, type, sql 
                FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            tables = []
            for row in cursor.fetchall():
                table_name, table_type, create_sql = row
                
                try:
                    # Get row count with timeout protection
                    cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` LIMIT 100000")  # Limit for performance
                    row_count_result = cursor.fetchone()
                    row_count = row_count_result[0] if row_count_result else 0
                    
                    # If count is at limit, show as "100k+"
                    if row_count >= 100000:
                        row_count = "100k+"
                    
                except sqlite3.Error:
                    row_count = "Unknown"
                
                tables.append({
                    "name": table_name,
                    "type": table_type,
                    "row_count": row_count,
                    "create_sql": create_sql
                })
            
            conn.close()
            return True, tables, f"Found {len(tables)} tables"
            
        except Exception as e:
            return False, [], f"Error retrieving SQLite tables: {str(e)}"

    @staticmethod
    def get_sqlite_columns(config: Dict[str, str], table_name: str, quick_mode: bool = True) -> Tuple[bool, List[Dict], str]:
        """Get columns for a specific SQLite table - ENHANCED"""
        try:
            db_path = config.get('database_path')
            if not db_path or not os.path.exists(db_path):
                return False, [], "Database file not found"
            
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA journal_mode = WAL")  # Performance optimization
            conn.execute("PRAGMA synchronous = NORMAL")  # Performance optimization
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table_name,))
            
            if not cursor.fetchone():
                conn.close()
                return False, [], f"Table '{table_name}' not found"
            
            # Get table info
            cursor.execute(f"PRAGMA table_info(`{table_name}`)")
            pragma_info = cursor.fetchall()
            
            # Get total row count once (with limit for performance)
            cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` LIMIT 50000")
            total_rows_result = cursor.fetchone()
            total_rows = total_rows_result[0] if total_rows_result else 0
            
            if total_rows >= 50000:
                total_rows = "50k+"
                is_large_table = True
            else:
                is_large_table = False
            
            columns = []
            for col_info in pragma_info:
                cid, name, data_type, not_null, default_value, pk = col_info
                
                # Categorize column type
                category = "unknown"
                if data_type.upper() in ["INTEGER", "INT"]:
                    category = "integer"
                elif data_type.upper() in ["REAL", "FLOAT", "DOUBLE"]:
                    category = "float"
                elif data_type.upper() in ["TEXT", "VARCHAR", "CHAR"]:
                    category = "string"
                elif data_type.upper() in ["DATETIME", "TIMESTAMP"]:
                    category = "timestamp"
                
                column_data = {
                    "name": name,
                    "type": data_type,
                    "data_type": data_type,  # Backward compatibility
                    "category": category,
                    "nullable": not bool(not_null),
                    "primary_key": bool(pk),
                    "default": default_value,
                    "default_value": default_value,  # Backward compatibility
                    "total_rows": total_rows
                }
                
                if quick_mode or is_large_table:
                    # Quick mode: minimal analysis for large tables
                    column_data.update({
                        "distinct_count": "Not analyzed",
                        "distinctness_ratio": 0,
                        "sample_values": [],
                        "suggested_for": SchemaDiscoveryService._get_sqlite_suggested_usage(name, data_type)
                    })
                else:
                    # Full analysis for smaller tables
                    try:
                        # Get sample values (limit to 3 for performance)
                        cursor.execute(f"SELECT `{name}` FROM `{table_name}` WHERE `{name}` IS NOT NULL LIMIT 3")
                        sample_values = [str(row[0]) for row in cursor.fetchall()]
                        
                        # Get distinct count (with reasonable limit)
                        cursor.execute(f"SELECT COUNT(DISTINCT `{name}`) as distinct_count FROM `{table_name}` LIMIT 10000")
                        distinct_count_result = cursor.fetchone()
                        distinct_count = distinct_count_result[0] if distinct_count_result else 0
                        
                        if isinstance(total_rows, int) and total_rows > 0:
                            distinctness_ratio = distinct_count / total_rows
                        else:
                            distinctness_ratio = 0
                        
                        column_data.update({
                            "distinct_count": distinct_count,
                            "distinctness_ratio": round(distinctness_ratio, 3),
                            "sample_values": sample_values,
                            "suggested_for": SchemaDiscoveryService._get_suggested_usage(category, distinctness_ratio)
                        })
                        
                    except sqlite3.Error:
                        # If analysis fails, fall back to simple classification
                        column_data.update({
                            "distinct_count": "Error",
                            "distinctness_ratio": 0,
                            "sample_values": [],
                            "suggested_for": SchemaDiscoveryService._get_sqlite_suggested_usage(name, data_type)
                        })
                
                columns.append(column_data)
            
            conn.close()
            message = f"Found {len(columns)} columns"
            if quick_mode or is_large_table:
                message += " (quick mode - limited analysis for performance)"
            
            return True, columns, message
            
        except Exception as e:
            return False, [], f"Error retrieving SQLite columns: {str(e)}"
    
    # =================== INFLUXDB METHODS (Enhanced from first implementation) ===================
    
    @staticmethod
    def get_influxdb_measurements_rest_api(config: Dict[str, str]) -> Tuple[bool, List[Dict], str]:
        """Get InfluxDB v2 measurements using REST API for fast schema discovery"""
        try:
            print("🔍 Starting InfluxDB schema discovery...")
            
            # Extract InfluxDB v2 connection parameters
            url = config.get('url', 'http://localhost:8086').rstrip('/')
            token = config.get('token')
            org = config.get('org', 'primary')
            bucket = config.get('bucket')
            
            # Validate required parameters
            if not token:
                return False, [], "Token is required for InfluxDB v2 connection"
            
            if not bucket:
                return False, [], "Bucket name is required for InfluxDB v2 connection"
            
            print(f"🔗 Connecting to InfluxDB at {url} for bucket '{bucket}'")
            
            # Get organization ID first
            org_id = SchemaDiscoveryService._get_org_id(url, token, org)
            if not org_id:
                return False, [], f"Could not find organization '{org}'"
            
            # Get bucket ID
            bucket_id = SchemaDiscoveryService._get_bucket_id(url, token, org_id, bucket)
            if not bucket_id:
                return False, [], f"Could not find bucket '{bucket}'"
            
            # Get measurements using query API (fast query)
            measurements = SchemaDiscoveryService._get_measurements_fast(url, token, org, bucket)
            if not measurements:
                return False, [], "No measurements found in bucket"
            
            print(f"📊 Found {len(measurements)} measurements")
            
            # Get field and tag info for each measurement
            enriched_measurements = []
            for i, measurement_name in enumerate(measurements[:50]):  # Limit to 50 measurements
                print(f"Analyzing measurement {i+1}/{min(len(measurements), 50)}: {measurement_name}")
                
                try:
                    field_count, tag_count = SchemaDiscoveryService._get_measurement_schema_fast(
                        url, token, org, bucket, measurement_name
                    )
                    
                    enriched_measurements.append({
                        "name": measurement_name,
                        "type": "measurement",
                        "bucket": bucket,
                        "field_count": field_count,
                        "tag_count": tag_count,
                        "sample_count": "N/A"  # Skip count for performance
                    })
                    
                except Exception as e:
                    print(f"Error getting schema for {measurement_name}: {e}")
                    enriched_measurements.append({
                        "name": measurement_name,
                        "type": "measurement",
                        "bucket": bucket,
                        "field_count": 0,
                        "tag_count": 0,
                        "sample_count": 0,
                        "error": str(e)[:100]
                    })
            
            return True, enriched_measurements, f"Found {len(enriched_measurements)} measurements"
            
        except Exception as e:
            return False, [], f"InfluxDB REST API error: {str(e)}"

    @staticmethod
    def get_influxdb_fields_rest_api(config: Dict[str, str], measurement: str) -> Tuple[bool, List[Dict], str]:
        """Get fields and tags for a specific InfluxDB measurement using REST API"""
        try:
            # Extract connection parameters
            url = config.get('url', 'http://localhost:8086').rstrip('/')
            token = config.get('token')
            org = config.get('org', 'primary')
            bucket = config.get('bucket')
            
            if not token or not bucket:
                return False, [], "Token and bucket are required"
            
            print(f"📊 Getting fields/tags for measurement '{measurement}'")
            
            columns = []
            
            # Add timestamp first
            columns.append({
                "name": "_time",
                "type": "timestamp",
                "category": "timestamp",
                "influx_type": "timestamp",
                "nullable": False,
                "measurement": measurement
            })
            
            # Get field keys
            field_query = f'''
            import "influxdata/influxdb/schema"
            schema.fieldKeys(bucket: "{bucket}", predicate: (r) => r._measurement == "{measurement}")
            '''
            
            field_result = SchemaDiscoveryService._execute_flux_query(url, token, org, field_query)
            field_names = set()
            for table in field_result:
                for record in table:
                    if '_value' in record and record['_value']:
                        field_names.add(record['_value'])
            
            # Add fields
            for field_name in sorted(field_names):
                columns.append({
                    "name": field_name,
                    "type": "number",
                    "category": "field",
                    "influx_type": "field",
                    "nullable": True,
                    "measurement": measurement
                })
            
            # Get tag keys
            tag_query = f'''
            import "influxdata/influxdb/schema"
            schema.tagKeys(bucket: "{bucket}", predicate: (r) => r._measurement == "{measurement}")
            '''
            
            tag_result = SchemaDiscoveryService._execute_flux_query(url, token, org, tag_query)
            tag_names = set()
            for table in tag_result:
                for record in table:
                    if '_value' in record and record['_value'] and record['_value'] not in ['_measurement', '_field']:
                        tag_names.add(record['_value'])
            
            # Add tags
            for tag_name in sorted(tag_names):
                columns.append({
                    "name": tag_name,
                    "type": "string",
                    "category": "tag",
                    "influx_type": "tag",
                    "nullable": True,
                    "measurement": measurement
                })
            
            print(f"✅ Found {len(field_names)} fields and {len(tag_names)} tags")
            
            return True, columns, f"Found {len(columns)} fields/tags for measurement '{measurement}'"
            
        except Exception as e:
            return False, [], f"Error retrieving InfluxDB fields: {str(e)}"

    # =================== INFLUXDB HELPER METHODS ===================
    
    @staticmethod
    def _get_org_id(url: str, token: str, org_name: str) -> Optional[str]:
        """Get organization ID by name"""
        try:
            headers = {
                'Authorization': f'Token {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{url}/api/v2/orgs", headers=headers, timeout=10)
            response.raise_for_status()
            
            orgs = response.json().get('orgs', [])
            for org in orgs:
                if org.get('name') == org_name:
                    return org.get('id')
            
            return None
            
        except Exception as e:
            print(f"Error getting org ID: {e}")
            return None

    @staticmethod
    def _get_bucket_id(url: str, token: str, org_id: str, bucket_name: str) -> Optional[str]:
        """Get bucket ID by name"""
        try:
            headers = {
                'Authorization': f'Token {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{url}/api/v2/buckets?orgID={org_id}", headers=headers, timeout=10)
            response.raise_for_status()
            
            buckets = response.json().get('buckets', [])
            for bucket in buckets:
                if bucket.get('name') == bucket_name:
                    return bucket.get('id')
            
            return None
            
        except Exception as e:
            print(f"Error getting bucket ID: {e}")
            return None

    @staticmethod
    def _get_measurements_fast(url: str, token: str, org: str, bucket: str) -> List[str]:
        """Get all measurements using a fast Flux query"""
        try:
            # Use simple Flux query to get measurements
            flux_query = f'''
            import "influxdata/influxdb/schema"
            schema.measurements(bucket: "{bucket}")
            '''
            
            measurements = SchemaDiscoveryService._execute_flux_query(url, token, org, flux_query)
            
            measurement_names = []
            for table in measurements:
                for record in table:
                    if '_value' in record:
                        measurement_names.append(record['_value'])
            
            return list(set(measurement_names))  # Remove duplicates
            
        except Exception as e:
            print(f"Error getting measurements: {e}")
            return []

    @staticmethod
    def _get_measurement_schema_fast(url: str, token: str, org: str, bucket: str, measurement: str) -> Tuple[int, int]:
        """Get field and tag counts for a measurement using fast queries"""
        try:
            # Get field keys
            field_query = f'''
            import "influxdata/influxdb/schema"
            schema.fieldKeys(bucket: "{bucket}", predicate: (r) => r._measurement == "{measurement}")
            '''
            
            field_result = SchemaDiscoveryService._execute_flux_query(url, token, org, field_query)
            field_names = set()
            for table in field_result:
                for record in table:
                    if '_value' in record:
                        field_names.add(record['_value'])
            
            # Get tag keys
            tag_query = f'''
            import "influxdata/influxdb/schema"
            schema.tagKeys(bucket: "{bucket}", predicate: (r) => r._measurement == "{measurement}")
            '''
            
            tag_result = SchemaDiscoveryService._execute_flux_query(url, token, org, tag_query)
            tag_names = set()
            for table in tag_result:
                for record in table:
                    if '_value' in record and record['_value'] not in ['_measurement', '_field']:
                        tag_names.add(record['_value'])
            
            return len(field_names), len(tag_names)
            
        except Exception as e:
            print(f"Error getting schema for {measurement}: {e}")
            return 0, 0

    @staticmethod
    def _execute_flux_query(url: str, token: str, org: str, query: str) -> List[List[Dict]]:
        """Execute a Flux query via REST API and return parsed results"""
        try:
            headers = {
                'Authorization': f'Token {token}',
                'Content-Type': 'application/vnd.flux',
                'Accept': 'application/csv'
            }
            
            response = requests.post(f"{url}/api/v2/query?org={org}", headers=headers, data=query, timeout=30)
            response.raise_for_status()
            
            # Parse CSV response
            import csv
            import io
            
            csv_data = response.text
            tables = []
            current_table = []
            
            for line in csv_data.split('\n'):
                if line.startswith('#') or not line.strip():
                    continue
                
                if line.startswith(',result,table'):
                    # New table header
                    if current_table:
                        tables.append(current_table)
                        current_table = []
                    continue
                
                # Parse data row
                reader = csv.reader([line])
                for row in reader:
                    if len(row) >= 4:  # Minimum expected columns
                        record = {}
                        try:
                            record['_result'] = row[1] if len(row) > 1 else ''
                            record['_table'] = row[2] if len(row) > 2 else ''
                            record['_value'] = row[3] if len(row) > 3 else ''
                            current_table.append(record)
                        except:
                            continue
            
            if current_table:
                tables.append(current_table)
            
            return tables
            
        except Exception as e:
            print(f"Error executing Flux query: {e}")
            return []
    
    # =================== PARQUET METHODS (Optimized from second implementation) ===================
    
    @staticmethod
    def get_parquet_tables(config: Dict[str, str]) -> Tuple[bool, List[Dict], str]:
        """Get all unique equipment tables from Parquet directory structure - OPTIMIZED"""
        try:
            base_path = config.get('base_path')
            if not base_path or not os.path.exists(base_path):
                return False, [], "Base path not found"
            
            # Discover all parquet files
            all_files = SchemaDiscoveryService._discover_all_parquet_files(base_path)
            
            if not all_files:
                return False, [], "No parquet files found in directory structure"
            
            # Group files by equipment type
            equipment_files = defaultdict(list)
            
            for file_path in all_files:
                equipment_name = SchemaDiscoveryService._extract_equipment_from_path(file_path)
                if equipment_name:
                    equipment_files[equipment_name].append(file_path)
            
            if not equipment_files:
                return False, [], "No valid equipment partitions found"
            
            # Create table information for each equipment type
            tables = []
            for equipment_name, files in equipment_files.items():
                try:
                    # Read a sample file to get basic info (compatibility fix)
                    sample_file = files[0]
                    try:
                        # Try pyarrow first for better performance
                        parquet_file = pq.ParquetFile(sample_file)
                        column_count = len(parquet_file.schema_arrow)
                    except Exception:
                        # Fallback to pandas
                        df_sample = pd.read_parquet(sample_file)
                        if len(df_sample) > 0:
                            df_sample = df_sample.head(1)  # Take first row only
                        column_count = len(df_sample.columns)
                    
                    # Estimate total rows across all dates (approximate)
                    estimated_rows = len(files) * 1000  # Rough estimate
                    
                    table_info = {
                        "name": equipment_name,
                        "type": "parquet_table",
                        "row_count": f"~{estimated_rows:,}",
                        "file_count": len(files),
                        "sample_file": sample_file,
                        "parquet_columns": column_count,
                        "base_path": base_path
                    }
                    
                    tables.append(table_info)
                    
                except Exception as e:
                    print(f"Error processing {equipment_name}: {str(e)}")
                    continue
            
            # Sort tables by name
            tables.sort(key=lambda x: x["name"])
            
            return True, tables, f"Found {len(tables)} equipment tables from {len(all_files)} parquet files"
            
        except Exception as e:
            return False, [], f"Error discovering parquet tables: {str(e)}"

    @staticmethod
    def get_parquet_columns(config: Dict[str, str], table_name: str, quick_mode: bool = False) -> Tuple[bool, List[Dict], str]:
        """Get columns for a specific parquet table (equipment type) - OPTIMIZED"""
        try:
            base_path = config.get('base_path')
            if not base_path or not os.path.exists(base_path):
                return False, [], "Base path not found"
            
            # Find files for this equipment
            equipment_files = SchemaDiscoveryService._find_equipment_files(base_path, table_name)
            
            if not equipment_files:
                return False, [], f"No parquet files found for equipment '{table_name}'"
            
            # Read schema from a representative file (compatibility fix)
            sample_file = equipment_files[0]
            try:
                # Method 1: Try pandas without nrows parameter
                df_sample = pd.read_parquet(sample_file)
                if not quick_mode and len(df_sample) > 100:
                    df_sample = df_sample.head(100)  # Limit to 100 rows for analysis
                elif quick_mode and len(df_sample) > 1:
                    df_sample = df_sample.head(1)   # Just 1 row for quick mode
            except Exception as e:
                return False, [], f"Error reading parquet file {sample_file}: {str(e)}"
            
            # Get partition information
            partition_info = SchemaDiscoveryService._extract_partition_info(equipment_files)
            
            columns = []
            
            # Add partition columns as filter columns
            for partition_col, values in partition_info.items():
                if partition_col not in ['year', 'month', 'day']:  # Skip timeline partitions
                    column_data = {
                        "name": partition_col,
                        "type": "partition_string",
                        "data_type": "partition_string",
                        "category": "categorical_text",
                        "nullable": False,
                        "primary_key": False,
                        "default_value": None,
                        "total_rows": len(equipment_files),
                        "distinct_count": len(values),
                        "distinctness_ratio": len(values) / len(equipment_files) if equipment_files else 0,
                        "sample_values": list(values)[:3],
                        "suggested_for": ["filters"],
                        "is_partition": True,
                        "partition_values": sorted(list(values))
                    }
                    columns.append(column_data)
            
            # Add parquet file columns
            for col_name in df_sample.columns:
                col_dtype = str(df_sample[col_name].dtype)
                
                if quick_mode:
                    # Quick analysis
                    column_data = {
                        "name": col_name,
                        "type": col_dtype,
                        "data_type": col_dtype,
                        "category": SchemaDiscoveryService._classify_parquet_column_simple(col_name, col_dtype),
                        "nullable": True,
                        "primary_key": False,
                        "default_value": None,
                        "total_rows": "~1M+",
                        "distinct_count": "Not analyzed",
                        "distinctness_ratio": 0,
                        "sample_values": [],
                        "suggested_for": SchemaDiscoveryService._get_parquet_suggested_usage(col_name, col_dtype),
                        "is_partition": False
                    }
                else:
                    # Detailed analysis
                    sample_values = df_sample[col_name].dropna().astype(str).tolist()[:3]
                    non_null_count = df_sample[col_name].notna().sum()
                    distinct_count = df_sample[col_name].nunique()
                    
                    distinctness_ratio = distinct_count / len(df_sample) if len(df_sample) > 0 else 0
                    
                    category = SchemaDiscoveryService._classify_parquet_column(col_name, col_dtype, distinctness_ratio, sample_values)
                    
                    column_data = {
                        "name": col_name,
                        "type": col_dtype,
                        "data_type": col_dtype,
                        "category": category,
                        "nullable": non_null_count < len(df_sample),
                        "primary_key": False,
                        "default_value": None,
                        "total_rows": f"~{len(equipment_files) * 1000:,}",
                        "distinct_count": distinct_count,
                        "distinctness_ratio": round(distinctness_ratio, 3),
                        "sample_values": sample_values,
                        "suggested_for": SchemaDiscoveryService._get_suggested_usage(category, distinctness_ratio),
                        "is_partition": False
                    }
                
                columns.append(column_data)
            
            message = f"Retrieved {len(columns)} columns for {table_name}"
            if quick_mode:
                message += " (quick mode)"
            
            return True, columns, message
            
        except Exception as e:
            return False, [], f"Error getting parquet columns: {str(e)}"

    # =================== PARQUET HELPER METHODS ===================
    
    @staticmethod
    def _discover_all_parquet_files(base_path: str) -> List[str]:
        """Discover all parquet files in the directory structure"""
        try:
            # Search pattern: base_path/**/equipment=*/dcu=*/*.parquet
            search_patterns = [
                os.path.join(base_path, "**", "equipment=*", "dcu=*", "*.parquet"),
                os.path.join(base_path, "**", "equipment=*", "*.parquet"),  # Alternative structure
                os.path.join(base_path, "**", "*.parquet")  # Simple structure
            ]
            
            all_files = []
            for pattern in search_patterns:
                files = glob.glob(pattern, recursive=True)
                all_files.extend(files)
                if files:  # If we found files with this pattern, stop searching
                    break
            
            return list(set(all_files))  # Remove duplicates
        except Exception as e:
            print(f"Error discovering files: {str(e)}")
            return []
    
    @staticmethod
    def _extract_equipment_from_path(file_path: str) -> Optional[str]:
        """Extract equipment name from file path"""
        try:
            # Split path and look for equipment= folder
            path_parts = file_path.split(os.sep)
            for part in path_parts:
                if part.startswith("equipment="):
                    return part.split("=")[1]
            
            # Fallback: try to extract from filename or directory structure
            filename = os.path.basename(file_path)
            if '.' in filename:
                equipment_name = filename.split('.')[0]
                if equipment_name and len(equipment_name) > 0:
                    return equipment_name
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def _find_equipment_files(base_path: str, equipment_name: str) -> List[str]:
        """Find all files for a specific equipment"""
        try:
            search_patterns = [
                os.path.join(base_path, "**", f"equipment={equipment_name}", "dcu=*", f"{equipment_name}.parquet"),
                os.path.join(base_path, "**", f"equipment={equipment_name}", "*.parquet"),
                os.path.join(base_path, "**", f"{equipment_name}.parquet"),
                os.path.join(base_path, "**", f"*{equipment_name}*.parquet")
            ]
            
            all_files = []
            for pattern in search_patterns:
                files = glob.glob(pattern, recursive=True)
                all_files.extend(files)
                if files:  # If we found files with this pattern, stop searching
                    break
            
            return list(set(all_files))  # Remove duplicates
        except Exception:
            return []
    
    @staticmethod
    def _extract_partition_info(file_paths: List[str]) -> Dict[str, Set[str]]:
        """Extract partition information from file paths"""
        partition_info = defaultdict(set)
        
        for file_path in file_paths:
            # Split path and extract partition key=value pairs
            path_parts = file_path.split(os.sep)
            for part in path_parts:
                if "=" in part and not part.startswith("."):
                    try:
                        key, value = part.split("=", 1)
                        if key and value:
                            partition_info[key].add(value)
                    except:
                        continue
        
        return dict(partition_info)
    
    @staticmethod
    def _classify_parquet_column_simple(col_name: str, col_dtype: str) -> str:
        """Simple column classification for parquet columns"""
        name_lower = col_name.lower()
        dtype_lower = col_dtype.lower()
        
        # Time-related columns
        if any(keyword in name_lower for keyword in ['time', 'date', 'timestamp', 'created', 'updated']):
            return "timestamp"
        
        # Numeric columns
        if any(dtype in dtype_lower for dtype in ['int', 'float', 'double', 'decimal']):
            if any(keyword in name_lower for keyword in ['id', '_id', 'count', 'index']):
                return "identifier"
            return "numeric"
        
        # Boolean columns
        if 'bool' in dtype_lower:
            return "boolean"
        
        # String/object columns
        if any(dtype in dtype_lower for dtype in ['object', 'string', 'category']):
            return "text"
        
        return "unknown"
    
    @staticmethod
    def _classify_parquet_column(col_name: str, col_dtype: str, distinctness_ratio: float, sample_values: List[str]) -> str:
        """Detailed column classification for parquet columns"""
        name_lower = col_name.lower()
        dtype_lower = col_dtype.lower()
        
        # Time-related columns
        if any(keyword in name_lower for keyword in ['time', 'date', 'timestamp', 'created', 'updated']):
            return "timestamp"
        
        # ID columns
        if any(keyword in name_lower for keyword in ['id', '_id', 'uuid', 'key']) or distinctness_ratio > 0.9:
            return "identifier"
        
        # Boolean columns
        if 'bool' in dtype_lower or all(val in ['0', '1', 'true', 'false', 'True', 'False'] for val in sample_values if val):
            return "boolean"
        
        # Numeric columns
        if any(dtype in dtype_lower for dtype in ['int', 'float', 'double', 'decimal']):
            if distinctness_ratio < 0.1:
                return "categorical_numeric"
            return "numeric"
        
        # String columns
        if any(dtype in dtype_lower for dtype in ['object', 'string', 'category']):
            if distinctness_ratio < 0.1:
                return "categorical_text"
            return "text"
        
        return "unknown"
    
    @staticmethod
    def _get_parquet_suggested_usage(col_name: str, col_dtype: str) -> List[str]:
        """Get suggested usage for parquet columns"""
        name_lower = col_name.lower()
        dtype_lower = col_dtype.lower()
        
        # Time columns
        if any(keyword in name_lower for keyword in ['time', 'date', 'timestamp']):
            return ["timestamp_field"]
        
        # Numeric columns - likely signals
        if any(dtype in dtype_lower for dtype in ['int', 'float', 'double', 'decimal']):
            if any(keyword in name_lower for keyword in ['voltage', 'current', 'temperature', 'pressure', 'power', 'energy', 'soc', 'soh']):
                return ["signals", "specs"]
            return ["signals"]
        
        # Boolean columns
        if 'bool' in dtype_lower:
            return ["signals", "specs"]
        
        # String columns
        return ["specs", "documentation"]
    
    # =================== COMMON UTILITY METHODS ===================
    
    @staticmethod
    def _get_sqlite_suggested_usage(col_name: str, data_type: str) -> List[str]:
        """Get suggested usage for SQLite columns"""
        name_lower = col_name.lower()
        data_type_lower = data_type.lower()
        
        # Time columns
        if any(keyword in name_lower for keyword in ['time', 'date', 'timestamp']):
            return ["timestamp_field"]
        
        # ID columns
        if any(keyword in name_lower for keyword in ['id', '_id', 'uuid', 'key']):
            return ["equipment_identifier"]
        
        # Numeric columns
        if data_type_lower in ['integer', 'int', 'real', 'numeric', 'decimal', 'float', 'double']:
            return ["signals", "specs"]
        
        # Boolean columns
        if data_type_lower in ['boolean', 'bool']:
            return ["signals", "specs"]
        
        # String columns
        return ["specs", "documentation"]
    
    @staticmethod
    def _get_suggested_usage(category: str, distinctness_ratio: float) -> List[str]:
        """Get suggested usage for UI (signals, filters, specs, etc.)"""
        suggestions = []
        
        if category == "timestamp":
            suggestions = ["timestamp_field"]
        elif category == "identifier":
            suggestions = ["equipment_identifier"]
        elif category == "boolean":
            suggestions = ["signals", "specs"]
        elif category == "numeric":
            suggestions = ["signals", "specs"]
        elif category == "categorical_numeric" or category == "categorical_text":
            suggestions = ["filters", "equipment_identifier"]
            if distinctness_ratio < 0.05:  # Very low distinctness
                suggestions.append("specs")
        elif category == "text":
            suggestions = ["specs", "documentation"]
        
        return suggestions
    
    # =================== MAIN SCHEMA DISCOVERY METHOD ===================
    
    @staticmethod
    def get_complete_schema(config: Dict[str, str], quick_mode: bool = True) -> Tuple[bool, Dict, str]:
        """
        Get complete schema for any database type - COMBINED IMPLEMENTATION
        Supports SQLite, Parquet, and InfluxDB with optimized performance
        """
        try:
            db_type = config.get('db_type', '').lower()
            print(f"🔍 Starting schema discovery for {db_type}")
            
            if db_type == "sqlite3":
                # SQLite implementation
                success, tables, message = SchemaDiscoveryService.get_sqlite_tables(config)
                if not success:
                    return False, {}, message
                
                schema = {
                    "database_info": {
                        "type": "sqlite3",
                        "path": config.get('database_path'),
                        "total_tables": len(tables),
                        "analysis_mode": "quick" if quick_mode else "full"
                    },
                    "tables": []
                }
                
                # Limit analysis to first 50 tables for performance
                max_tables = 50 if quick_mode else len(tables)
                analyzed_tables = tables[:max_tables]
                
                # Get columns for each table
                for i, table in enumerate(analyzed_tables):
                    print(f"Analyzing table {i+1}/{len(analyzed_tables)}: {table['name']}")
                    
                    # Use quick mode for large tables or when requested
                    use_quick_mode = quick_mode or (isinstance(table['row_count'], str) and 'k+' in str(table['row_count']))
                    
                    success, columns, _ = SchemaDiscoveryService.get_sqlite_columns(
                        config, table["name"], quick_mode=use_quick_mode
                    )
                    if success:
                        table["columns"] = columns
                        table["total_columns"] = len(columns)
                        
                        # Add column type summary
                        column_types = {}
                        for col in columns:
                            col_type = col["category"]
                            column_types[col_type] = column_types.get(col_type, 0) + 1
                        table["column_type_summary"] = column_types
                    
                    schema["tables"].append(table)
                
                if len(tables) > max_tables:
                    schema["database_info"]["note"] = f"Showing first {max_tables} tables of {len(tables)} total"
                
                return True, schema, f"SQLite schema retrieved successfully. {len(analyzed_tables)} tables analyzed"
            
            elif db_type == "influxdb":
                # InfluxDB v2 REST API implementation
                success, measurements, message = SchemaDiscoveryService.get_influxdb_measurements_rest_api(config)
                
                if not success:
                    return False, {}, message
                
                schema = {
                    "database_info": {
                        "type": "influxdb",
                        "url": config.get('url'),
                        "org": config.get('org'),
                        "bucket": config.get('bucket'),
                        "total_measurements": len(measurements),
                        "analysis_mode": "quick" if quick_mode else "full"
                    },
                    "measurements": []  # Note: "measurements" instead of "tables" for InfluxDB
                }
                
                # Get fields and tags for each measurement
                max_measurements = 25 if quick_mode else len(measurements)
                analyzed_measurements = measurements[:max_measurements]
                
                for i, measurement in enumerate(analyzed_measurements):
                    print(f"Analyzing measurement {i+1}/{len(analyzed_measurements)}: {measurement['name']}")
                    
                    success, fields, _ = SchemaDiscoveryService.get_influxdb_fields_rest_api(
                        config, measurement["name"]
                    )
                    if success:
                        measurement["fields"] = fields
                        measurement["total_fields"] = len([f for f in fields if f["category"] == "field"])
                        measurement["total_tags"] = len([f for f in fields if f["category"] == "tag"])
                        
                        # Add field type summary
                        field_types = {}
                        for field in fields:
                            field_category = field["category"]
                            field_types[field_category] = field_types.get(field_category, 0) + 1
                        measurement["field_type_summary"] = field_types
                    
                    schema["measurements"].append(measurement)
                
                if len(measurements) > max_measurements:
                    schema["database_info"]["note"] = f"Showing first {max_measurements} measurements of {len(measurements)} total"
                
                return True, schema, f"InfluxDB schema retrieved successfully. {len(analyzed_measurements)} measurements analyzed"
            
            elif db_type == "parquet":
                # Parquet implementation
                success, tables, message = SchemaDiscoveryService.get_parquet_tables(config)
                if not success:
                    return False, {}, message
                
                schema = {
                    "database_info": {
                        "type": "parquet",
                        "base_path": config.get('base_path'),
                        "total_equipment_groups": len(tables),
                        "analysis_mode": "quick" if quick_mode else "full"
                    },
                    "tables": []
                }
                
                # Get columns for each equipment group
                for i, table in enumerate(tables):
                    print(f"Analyzing parquet table {i+1}/{len(tables)}: {table['name']}")
                    
                    success, columns, _ = SchemaDiscoveryService.get_parquet_columns(
                        config, table["name"], quick_mode=quick_mode
                    )
                    if success:
                        table["columns"] = columns
                        table["total_columns"] = len(columns)
                        
                        # Add column type summary
                        column_types = {}
                        partition_columns = 0
                        parquet_columns = 0
                        
                        for col in columns:
                            col_type = col["category"]
                            column_types[col_type] = column_types.get(col_type, 0) + 1
                            
                            if col.get("is_partition", False):
                                partition_columns += 1
                            else:
                                parquet_columns += 1
                        
                        table["column_type_summary"] = column_types
                        table["partition_columns"] = partition_columns
                        table["parquet_columns"] = parquet_columns
                    
                    schema["tables"].append(table)
                
                return True, schema, f"Parquet schema retrieved successfully from {config.get('base_path')}"
            
            else:
                return False, {}, f"Unsupported database type: {db_type}"
            
        except Exception as e:
            return False, {}, f"Error retrieving schema: {str(e)}"
    
    # =================== PERFORMANCE AND DEBUG METHODS ===================
    
    @staticmethod
    def test_connection_schema(config: Dict[str, str]) -> Tuple[bool, Dict, str]:
        """Test connection and get basic schema info quickly"""
        try:
            db_type = config.get('db_type', '').lower()
            
            if db_type == "sqlite3":
                db_path = config.get('database_path')
                if not db_path or not os.path.exists(db_path):
                    return False, {}, "Database file not found"
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                conn.close()
                
                return True, {"type": "sqlite3", "table_count": table_count}, "SQLite connection successful"
            
            elif db_type == "influxdb":
                url = config.get('url', 'http://localhost:8086').rstrip('/')
                token = config.get('token')
                org = config.get('org', 'primary')
                
                if not token:
                    return False, {}, "Token is required"
                
                # Test basic connectivity
                headers = {'Authorization': f'Token {token}'}
                response = requests.get(f"{url}/api/v2/orgs", headers=headers, timeout=5)
                response.raise_for_status()
                
                return True, {"type": "influxdb", "connection": "successful"}, "InfluxDB connection successful"
            
            elif db_type == "parquet":
                base_path = config.get('base_path')
                if not base_path or not os.path.exists(base_path):
                    return False, {}, "Base path not found"
                
                # Quick file count
                parquet_files = glob.glob(os.path.join(base_path, "**", "*.parquet"), recursive=True)
                file_count = len(parquet_files)
                
                return True, {"type": "parquet", "file_count": file_count}, "Parquet path accessible"
            
            else:
                return False, {}, f"Unsupported database type: {db_type}"
                
        except Exception as e:
            return False, {}, f"Connection test failed: {str(e)}"
    
    @staticmethod
    def get_schema_summary(config: Dict[str, str]) -> Tuple[bool, Dict, str]:
        """Get a quick schema summary without detailed analysis"""
        try:
            success, schema, message = SchemaDiscoveryService.get_complete_schema(config, quick_mode=True)
            
            if not success:
                return False, {}, message
            
            # Create summary
            db_info = schema.get("database_info", {})
            db_type = db_info.get("type", "unknown")
            
            if db_type == "influxdb":
                measurements = schema.get("measurements", [])
                summary = {
                    "type": "influxdb",
                    "total_measurements": len(measurements),
                    "total_fields": sum(m.get("total_fields", 0) for m in measurements),
                    "total_tags": sum(m.get("total_tags", 0) for m in measurements),
                    "sample_measurements": [m["name"] for m in measurements[:5]]
                }
            else:
                tables = schema.get("tables", [])
                summary = {
                    "type": db_type,
                    "total_tables": len(tables),
                    "total_columns": sum(t.get("total_columns", 0) for t in tables),
                    "sample_tables": [t["name"] for t in tables[:5]]
                }
            
            return True, summary, "Schema summary generated successfully"
            
        except Exception as e:
            return False, {}, f"Error generating schema summary: {str(e)}"

# =================== CONNECTION-BASED SCHEMA DISCOVERY ===================

def get_schema_for_connection(db: Session, connection_id: str, table_name: str = None):
    """Get schema information for a specific connection - ENHANCED"""
    try:
        # Get connection
        connection = crud.get_data_connection_by_id(db, connection_id)
        if not connection:
            return False, {}, "Connection not found"
        
        if connection.status != "active":
            return False, {}, "Connection is not active"
        
        # Get connection config
        config = crud.get_connection_config_dict(db, connection_id)
        if not config:
            return False, {}, "Connection configuration not found"
        
        # Add db_type to config for schema discovery
        config['db_type'] = connection.db_type
        
        # Route to appropriate schema discovery method
        if connection.db_type.lower() == "sqlite3":
            if table_name:
                return SchemaDiscoveryService.get_sqlite_columns(config, table_name)
            else:
                return SchemaDiscoveryService.get_sqlite_tables(config)
        elif connection.db_type.lower() == "parquet":
            if table_name:
                return SchemaDiscoveryService.get_parquet_columns(config, table_name)
            else:
                return SchemaDiscoveryService.get_parquet_tables(config)
        elif connection.db_type.lower() == "influxdb":
            if table_name:
                return SchemaDiscoveryService.get_influxdb_fields_rest_api(config, table_name)
            else:
                return SchemaDiscoveryService.get_influxdb_measurements_rest_api(config)
        else:
            return False, {}, f"Unsupported database type: {connection.db_type}"
            
    except Exception as e:
        return False, {}, f"Schema discovery error: {str(e)}"