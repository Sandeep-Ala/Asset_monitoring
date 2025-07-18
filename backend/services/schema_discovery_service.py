# services/schema_discovery_service.py - InfluxDB v2 REST API Implementation

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

# InfluxDB v2 imports (keeping for potential fallback)
try:
    from influxdb_client import InfluxDBClient, QueryApi
    from influxdb_client.rest import ApiException
    INFLUXDB_AVAILABLE = True
except ImportError:
    INFLUXDB_AVAILABLE = False
    InfluxDBClient = None
    QueryApi = None
    ApiException = Exception

class SchemaDiscoveryService:
    """Service to discover database schema for different database types"""
    
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
        """Get columns for a specific SQLite table"""
        try:
            db_path = config.get('database_path')
            if not db_path or not os.path.exists(db_path):
                return False, [], "Database file not found"
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute(f"PRAGMA table_info(`{table_name}`)")
            columns = []
            
            for row in cursor.fetchall():
                cid, name, data_type, notnull, default_value, pk = row
                
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
                
                columns.append({
                    "name": name,
                    "type": data_type,
                    "category": category,
                    "nullable": not bool(notnull),
                    "primary_key": bool(pk),
                    "default": default_value
                })
            
            conn.close()
            return True, columns, f"Found {len(columns)} columns"
            
        except Exception as e:
            return False, [], f"Error retrieving SQLite columns: {str(e)}"

    @staticmethod
    def get_influxdb_measurements_rest_api(config: Dict[str, str]) -> Tuple[bool, List[Dict], str]:
        """Get InfluxDB v2 measurements using REST API for fast schema discovery"""
        try:
            # Extract InfluxDB v2 connection parameters
            url = config.get('url', 'http://localhost:8086')
            token = config.get('token')
            org = config.get('org', 'primary')
            bucket = config.get('bucket')
            
            # Clean URL (remove trailing slash)
            
            # Validate required parameters
            if not token:
                return False, [], "Token is required for InfluxDB v2 connection"
            
            if not bucket:
                return False, [], "Bucket name is required for InfluxDB v2 connection"
            
            print(f"🔍 Getting InfluxDB schema from {url} for bucket '{bucket}'")
            
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
            schema.fieldKeys(bucket: "{bucket}",predicate: (r) => r._measurement == "{measurement}")
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
            
            data = {
                'query': query,
                'org': org
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
            
            print(f" Getting fields/tags for measurement '{measurement}'")
            
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
            schema.tagKeys(bucket: "{bucket}",predicate: (r) => r._measurement == "{measurement}")
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
            
            print(f" Found {len(field_names)} fields and {len(tag_names)} tags")
            
            return True, columns, f"Found {len(columns)} fields/tags for measurement '{measurement}'"
            
        except Exception as e:
            return False, [], f"Error retrieving InfluxDB fields: {str(e)}"

    # Keep existing methods for other database types...
    @staticmethod
    def get_parquet_tables(config: Dict[str, str]) -> Tuple[bool, List[Dict], str]:
        """Get parquet files structure (equivalent to tables)"""
        try:
            base_path = config.get('base_path')
            if not base_path or not os.path.exists(base_path):
                return False, [], "Base path not found"
            
            # Discover parquet files
            parquet_files = glob.glob(os.path.join(base_path, "**", "*.parquet"), recursive=True)
            
            if not parquet_files:
                return False, [], "No parquet files found"
            
            # Group by equipment type
            equipment_groups = defaultdict(list)
            for file_path in parquet_files:
                # Extract equipment from path
                path_parts = file_path.replace(base_path, "").split(os.sep)
                equipment = "unknown"
                for part in path_parts:
                    if part.startswith("equipment="):
                        equipment = part.split("=")[1]
                        break
                equipment_groups[equipment].append(file_path)
            
            tables = []
            for equipment, files in equipment_groups.items():
                tables.append({
                    "name": equipment,
                    "type": "equipment_group",
                    "file_count": len(files),
                    "sample_file": files[0] if files else None
                })
            
            return True, tables, f"Found {len(tables)} equipment groups"
            
        except Exception as e:
            return False, [], f"Error retrieving parquet structure: {str(e)}"

    @staticmethod
    def get_parquet_columns(config: Dict[str, str], equipment_name: str) -> Tuple[bool, List[Dict], str]:
        """Get columns from parquet files for specific equipment"""
        try:
            base_path = config.get('base_path')
            if not base_path or not os.path.exists(base_path):
                return False, [], "Base path not found"
            
            # Find parquet files for this equipment
            pattern = os.path.join(base_path, "**", f"equipment={equipment_name}", "**", "*.parquet")
            files = glob.glob(pattern, recursive=True)
            
            if not files:
                return False, [], f"No parquet files found for equipment: {equipment_name}"
            
            # Read sample file to get schema
            sample_file = files[0]
            df = pd.read_parquet(sample_file, engine='pyarrow')
            
            columns = []
            for col_name in df.columns:
                col_type = str(df[col_name].dtype)
                
                # Categorize column type
                category = "unknown"
                if "int" in col_type:
                    category = "integer"
                elif "float" in col_type:
                    category = "float"
                elif "object" in col_type or "string" in col_type:
                    category = "string"
                elif "datetime" in col_type:
                    category = "timestamp"
                
                columns.append({
                    "name": col_name,
                    "type": col_type,
                    "category": category,
                    "nullable": True,
                    "equipment": equipment_name
                })
            
            return True, columns, f"Found {len(columns)} columns"
            
        except Exception as e:
            return False, [], f"Error retrieving parquet columns: {str(e)}"

    @staticmethod
    def get_complete_schema(config: Dict[str, str], quick_mode: bool = True) -> Tuple[bool, Dict, str]:
        """Get complete schema for any database type"""
        try:
            db_type = config.get('db_type', '').lower()
            
            if db_type == "sqlite3":
                # SQLite implementation (existing)
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
                    
                    success, columns, _ = SchemaDiscoveryService.get_sqlite_columns(
                        config, table["name"], quick_mode=quick_mode
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
                print(schema)
                # Get fields and tags for each measurement
                for i, measurement in enumerate(measurements):
                    print(f"Analyzing measurement {i+1}/{len(measurements)}: {measurement['name']}")
                    
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
                
                return True, schema, f"InfluxDB schema retrieved successfully. {len(measurements)} measurements analyzed"
            
            elif db_type == "parquet":
                # Parquet implementation (existing)
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
                for table in tables:
                    success, columns, _ = SchemaDiscoveryService.get_parquet_columns(
                        config, table["name"]
                    )
                    if success:
                        table["columns"] = columns
                        table["total_columns"] = len(columns)
                    
                    schema["tables"].append(table)
                
                return True, schema, f"Parquet schema retrieved successfully from {config.get('base_path')}"
            
            else:
                return False, {}, f"Unsupported database type: {db_type}"
            
        except Exception as e:
            return False, {}, f"Error retrieving schema: {str(e)}"

def get_schema_for_connection(db: Session, connection_id: str, table_name: str = None):
    """Get schema information for a specific connection"""
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