# services/data_retrieval_service.py - COMBINED InfluxDB + Parquet + SQLite Implementation
# Optimized for Chart.js with proper ISO timestamps and enhanced error handling

import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import duckdb
import sqlite3
from services.widget_crud import get_widget_by_id, widget_to_dict
from services.query_generation_service import QueryGenerationService
import services.datasource_crud as datasource_crud
from models.meta_models import EquipmentSignal
from config import get_db

# InfluxDB v2 imports
try:
    from influxdb_client import InfluxDBClient, QueryApi
    from influxdb_client.rest import ApiException
    import requests
    INFLUXDB_AVAILABLE = True
    print("✅ InfluxDB client library available")
except ImportError:
    INFLUXDB_AVAILABLE = False
    InfluxDBClient = None
    QueryApi = None
    ApiException = Exception
    requests = None
    print("⚠️ InfluxDB client library not installed")

class DataRetrievalService:
    """
    Enhanced service for widget data retrieval with Chart.js compatible timestamps
    Supports SQLite, Parquet, and InfluxDB v2 data sources with robust error handling
    
    COMBINED IMPLEMENTATION:
    - InfluxDB v2 with REST API fallback and comprehensive error handling
    - Optimized Parquet/SQLite processing with efficient timestamp handling
    - Chart.js optimized formatting with proper ISO timestamps
    - Backward compatibility with existing functionality
    """
    
    @staticmethod
    def format_data_for_chart(data_rows: List[Dict], widget_config: Dict) -> Dict:
        """
        Format database query results for Chart.js with proper ISO timestamps
        COMBINED: Enhanced for InfluxDB compatibility + Parquet optimization
        """
        try:
            print(f"🔧 Formatting {len(data_rows)} data rows for Chart.js...")
            
            if not data_rows:
                print("📊 No data rows to format")
                return {
                    "labels": [],
                    "datasets": [],
                    "isEmpty": True,
                    "totalPoints": 0,
                    "timeRange": None
                }
            
            # Sort data by timestamp first (optimized from both implementations)
            sorted_data_rows = DataRetrievalService._sort_data_by_timestamp(data_rows)
            
            # Initialize data structures
            labels = []
            signal_data = {}
            
            # Get signal configuration
            signal_ids = widget_config.get('signal_ids', [])
            
            # Get signal metadata if needed (optimized batch query)
            if signal_ids and isinstance(signal_ids[0], int):
                signal_metadata = DataRetrievalService._get_signal_metadata_from_db(signal_ids)
            else:
                signal_metadata = signal_ids
            
            print(f"📡 Processing {len(signal_metadata)} signals...")
            
            # Pre-compute available signal columns for efficiency (from Parquet optimization)
            available_columns = list(sorted_data_rows[0].keys()) if sorted_data_rows else []
            signal_columns = [col for col in available_columns 
                            if col not in ['timestamp', '_time', 't_sampling_time', 'bucket_time', 'time']]
            
            # Process each data row
            for row in sorted_data_rows:
                # CRITICAL IMPROVEMENT: Extract and send full ISO timestamp
                timestamp = DataRetrievalService._extract_timestamp(row)
                if timestamp:
                    # Send ISO format timestamp that Chart.js can directly parse
                    iso_timestamp = timestamp.isoformat()
                    labels.append(iso_timestamp)
                    
                    # Extract signal values efficiently (optimized method)
                    if signal_metadata:
                        DataRetrievalService._extract_signal_values_optimized(
                            row, signal_metadata, signal_columns, signal_data
                        )
                    else:
                        # Fallback: extract all numeric columns
                        DataRetrievalService._extract_numeric_values(row, signal_data)
                else:
                    print(f"⚠️ Skipping row without timestamp: {list(row.keys())}")
                    continue
            
            # Create datasets with optimized color assignment
            datasets = DataRetrievalService._create_datasets(signal_data, len(labels))
            
            # Calculate time range with full ISO timestamps
            time_range = DataRetrievalService._calculate_time_range_iso(sorted_data_rows)
            
            result = {
                "labels": labels,  # Now contains ISO timestamps like "2025-03-01T07:50:00"
                "datasets": datasets,
                "isEmpty": len(labels) == 0,
                "totalPoints": len(labels),
                "timeRange": time_range,
                "signalCount": len(datasets),
                "formatTimestamp": datetime.now().isoformat()
            }
            
            # Add debug info for first few timestamps
            if len(labels) > 0:
                print(f"✅ Chart data formatted with ISO timestamps:")
                print(f"   - Total points: {len(labels)}")
                print(f"   - First timestamp: {labels[0]}")
                print(f"   - Last timestamp: {labels[-1] if labels else 'None'}")
                print(f"   - Datasets: {len(datasets)}")
            
            return result
            
        except Exception as e:
            print(f"💥 Chart formatting error: {str(e)}")
            return {
                "labels": [],
                "datasets": [],
                "isEmpty": True,
                "totalPoints": 0,
                "timeRange": None,
                "error": f"Chart formatting failed: {str(e)}"
            }
    
    @staticmethod
    def execute_widget_query(query: str, data_source_type: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute query based on data source type and return results - ENHANCED"""
        try:
            print(f"🚀 Executing {data_source_type} query...")
            print(f"📝 Query preview: {query[:100]}...")
            
            # Normalize data source type
            data_source_type_lower = data_source_type.lower()
            
            if data_source_type_lower in ["sqlite3", "sqlite"]:
                return DataRetrievalService._execute_sqlite_query(query, connection_config)
            elif data_source_type_lower == "parquet":
                return DataRetrievalService._execute_parquet_query(query, connection_config)
            elif data_source_type_lower == "influxdb":
                return DataRetrievalService._execute_influxdb_query(query, connection_config)
            else:
                return False, [], f"Unsupported data source type: {data_source_type}"
                
        except Exception as e:
            return False, f"Time range validation error: {str(e)}"

    @staticmethod
    def get_data_source_status(db: Session, connection_id: str = None) -> Dict[str, Any]:
        """
        Get status of data source connection
        COMBINED: Enhanced for all data source types
        """
        try:
            print(f"🔍 Checking data source status...")
            
            if connection_id:
                connection = datasource_crud.get_data_connection_by_id(db, connection_id)
                if not connection:
                    return {"status": "error", "message": "Connection not found"}
                connections = [connection]
            else:
                connections = datasource_crud.get_all_data_connections(db)
            
            status_info = {
                "total_connections": len(connections),
                "active_connections": sum(1 for conn in connections if conn.status == 'active'),
                "connections": []
            }
            
            for conn in connections:
                conn_status = {
                    "id": conn.id,
                    "name": conn.name,
                    "db_type": conn.db_type,
                    "status": conn.status,
                    "last_tested": getattr(conn, 'last_tested', None)
                }
                
                # Add type-specific status information
                if conn.db_type.lower() == 'influxdb':
                    if INFLUXDB_AVAILABLE:
                        conn_status["influxdb_client_available"] = True
                        # Could add connection test here
                    else:
                        conn_status["influxdb_client_available"] = False
                        conn_status["warning"] = "InfluxDB client library not installed"
                
                status_info["connections"].append(conn_status)
            
            return status_info
        except Exception as e:
            return {"status": "error", "message": f"Status check error: {str(e)}"}

    @staticmethod
    def test_connection(db: Session, connection_id: str) -> Dict[str, Any]:
        """
        Test data source connection
        COMBINED: Test connectivity for all supported data source types
        """
        try:
            print(f"🧪 Testing connection: {connection_id}")
            
            connection = datasource_crud.get_data_connection_by_id(db, connection_id)
            if not connection:
                return {"success": False, "message": "Connection not found"}
            
            connection_config = datasource_crud.get_connection_config_dict(db, connection_id)
            data_source_type = connection.db_type.lower()
            
            if data_source_type == 'sqlite3' or data_source_type == 'sqlite':
                return DataRetrievalService._test_sqlite_connection(connection_config)
            elif data_source_type == 'parquet':
                return DataRetrievalService._test_parquet_connection(connection_config)
            elif data_source_type == 'influxdb':
                return DataRetrievalService._test_influxdb_connection(connection_config)
            else:
                return {"success": False, "message": f"Unsupported data source type: {data_source_type}"}
                
        except Exception as e:
            return {"success": False, "message": f"Connection test error: {str(e)}"}

    @staticmethod
    def _test_sqlite_connection(connection_config: Dict) -> Dict[str, Any]:
        """Test SQLite connection"""
        try:
            db_path = connection_config.get('database_path') or connection_config.get('db_path', '')
            if not db_path:
                return {"success": False, "message": "Database path not configured"}
            
            import os
            if not os.path.exists(db_path):
                return {"success": False, "message": f"Database file not found: {db_path}"}
            
            # Test basic connectivity
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            
            return {
                "success": True, 
                "message": "SQLite connection successful",
                "details": {"has_tables": result is not None}
            }
            
        except Exception as e:
            return {"success": False, "message": f"SQLite connection failed: {str(e)}"}

    @staticmethod
    def _test_parquet_connection(connection_config: Dict) -> Dict[str, Any]:
        """Test Parquet connection"""
        try:
            file_path = connection_config.get('file_path', '')
            if not file_path:
                return {"success": False, "message": "File path not configured"}
            
            import os
            if not os.path.exists(file_path):
                return {"success": False, "message": f"Parquet file not found: {file_path}"}
            
            # Test basic connectivity with DuckDB
            conn = duckdb.connect()
            result = conn.execute(f"SELECT COUNT(*) FROM read_parquet('{file_path}') LIMIT 1").fetchone()
            row_count = result[0] if result else 0
            
            return {
                "success": True, 
                "message": "Parquet connection successful",
                "details": {"row_count": row_count}
            }
            
        except Exception as e:
            return {"success": False, "message": f"Parquet connection failed: {str(e)}"}

    @staticmethod
    def _test_influxdb_connection(connection_config: Dict) -> Dict[str, Any]:
        """Test InfluxDB connection"""
        try:
            if not INFLUXDB_AVAILABLE:
                return {
                    "success": False, 
                    "message": "InfluxDB client library not installed. Install with: pip install influxdb-client"
                }
            
            url = connection_config.get('url', 'http://localhost:8086')
            token = connection_config.get('token')
            org = connection_config.get('org', 'primary')
            
            if not token:
                return {"success": False, "message": "InfluxDB token not configured"}
            
            # Test connectivity using REST API
            health_url = f"{url.rstrip('/')}/health"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code != 200:
                return {"success": False, "message": f"InfluxDB health check failed: {response.status_code}"}
            
            # Test query access
            try:
                with InfluxDBClient(url=url, token=token, org=org, timeout=10_000) as client:
                    # Try to list buckets as a connectivity test
                    buckets_api = client.buckets_api()
                    buckets = buckets_api.find_buckets()
                    bucket_count = len(buckets.buckets) if buckets and buckets.buckets else 0
                    
                return {
                    "success": True, 
                    "message": "InfluxDB connection successful",
                    "details": {
                        "org": org,
                        "bucket_count": bucket_count,
                        "influx_version": "v2"
                    }
                }
                
            except ApiException as e:
                if e.status == 403:
                    return {"success": False, "message": "InfluxDB authentication failed. Check token permissions."}
                elif e.status == 404:
                    return {"success": False, "message": "InfluxDB organization not found."}
                else:
                    return {"success": False, "message": f"InfluxDB API error: {str(e)}"}
                    
        except Exception as e:
            return {"success": False, "message": f"InfluxDB connection failed: {str(e)}"}

    # =================== UTILITY METHODS ===================

    @staticmethod
    def get_supported_data_sources() -> List[Dict[str, str]]:
        """Get list of supported data source types"""
        data_sources = [
            {"type": "sqlite3", "name": "SQLite Database", "description": "Local SQLite database files"},
            {"type": "parquet", "name": "Parquet Files", "description": "Columnar data files via DuckDB"}
        ]
        
        if INFLUXDB_AVAILABLE:
            data_sources.append({
                "type": "influxdb", 
                "name": "InfluxDB v2", 
                "description": "Time series database with Flux query language"
            })
        else:
            data_sources.append({
                "type": "influxdb", 
                "name": "InfluxDB v2 (Not Available)", 
                "description": "Install influxdb-client to enable InfluxDB support"
            })
        
        return data_sources

    @staticmethod
    def calculate_data_points_estimate(time_range: Dict, window_period: str) -> Dict[str, Any]:
        """Calculate estimated data points for given time range and window period"""
        try:
            start_dt = pd.to_datetime(time_range.get('start'))
            end_dt = pd.to_datetime(time_range.get('end'))
            duration_seconds = (end_dt - start_dt).total_seconds()
            
            # Map window periods to seconds
            window_seconds_map = {
                "1m": 60,
                "5m": 300,
                "15m": 900,
                "1h": 3600,
                "6h": 21600,
                "1d": 86400
            }
            
            window_seconds = window_seconds_map.get(window_period, 3600)  # Default to 1 hour
            estimated_points = int(duration_seconds / window_seconds)
            
            return {
                "estimated_points": estimated_points,
                "duration_hours": duration_seconds / 3600,
                "window_seconds": window_seconds,
                "window_period": window_period,
                "is_optimal": estimated_points <= MAX_POINTS_PER_WIDGET if 'MAX_POINTS_PER_WIDGET' in globals() else estimated_points <= 100
            }
            
        except Exception as e:
            return {
                "estimated_points": 0,
                "error": f"Estimation failed: {str(e)}"
            }

    @staticmethod
    def get_query_performance_stats() -> Dict[str, Any]:
        """Get query performance statistics (can be enhanced with actual metrics)"""
        return {
            "average_query_time": {
                "sqlite": "< 1s",
                "parquet": "< 2s", 
                "influxdb": "< 3s"
            },
            "supported_operations": {
                "time_aggregation": True,
                "filtering": True,
                "multi_signal": True,
                "time_range_queries": True
            },
            "limitations": {
                "max_points_per_widget": 100,  # From config
                "max_time_range_days": 365,
                "concurrent_queries": 10
            }
        }, [], f"Query execution error: {str(e)}"
    
    # =================== INFLUXDB METHODS (Enhanced from first implementation) ===================
    
    @staticmethod
    def _execute_influxdb_query(query: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute InfluxDB v2 Flux query - ENHANCED VERSION with REST API fallback"""
        
        if not INFLUXDB_AVAILABLE:
            return False, [], "InfluxDB client library not installed. Please install: pip install influxdb-client"
        
        try:
            print("🏗️ Executing InfluxDB Flux query...")
            
            # Extract connection parameters
            url = connection_config.get('url', 'http://localhost:8086')
            token = connection_config.get('token')
            org = connection_config.get('org', 'primary')
            
            if not token:
                return False, [], "InfluxDB token not found in connection config"
            
            print(f"🔗 Connecting to InfluxDB at {url} (org: {org})")
            
            # Try using REST API first (more reliable)
            try:
                return DataRetrievalService._execute_influxdb_rest_api(query, connection_config)
            except Exception as rest_error:
                print(f"⚠️ REST API failed, trying client library: {str(rest_error)}")
                
                # Fallback to client library
                with InfluxDBClient(url=url, token=token, org=org, timeout=30_000) as client:
                    query_api = client.query_api()
                    
                    try:
                        print("📊 Executing Flux query via client library...")
                        
                        # Execute Flux query
                        result = query_api.query(query)
                        
                        # Convert result to list of dictionaries
                        data_rows = []
                        for table in result:
                            for record in table.records:
                                # Build row dictionary
                                row = {}
                                
                                # Add timestamp
                                if record.get_time():
                                    row['_time'] = record.get_time().isoformat()
                                
                                # Add all fields from the record
                                values = record.values
                                for key, value in values.items():
                                    if key not in ['result', 'table', '_start', '_stop']:
                                        row[key] = value
                                
                                data_rows.append(row)
                        
                        print(f"✅ InfluxDB query executed successfully: {len(data_rows)} rows returned")
                        return True, data_rows, ""
                        
                    except ApiException as e:
                        if e.status == 400:
                            error_msg = f"Invalid Flux query syntax: {str(e)}"
                        elif e.status == 403:
                            error_msg = "Insufficient permissions to query InfluxDB. Check token permissions."
                        elif e.status == 404:
                            error_msg = "InfluxDB bucket or measurement not found. Check connection config."
                        else:
                            error_msg = f"InfluxDB API error (status {e.status}): {str(e)}"
                        
                        print(f"❌ InfluxDB API Error: {error_msg}")
                        return False, [], error_msg
                        
                    except Exception as e:
                        error_msg = f"InfluxDB query execution failed: {str(e)}"
                        print(f"❌ InfluxDB Execution Error: {error_msg}")
                        return False, [], error_msg
                    
        except Exception as e:
            error_msg = f"InfluxDB connection error: {str(e)}"
            print(f"❌ InfluxDB Connection Error: {error_msg}")
            return False, [], error_msg
    
    @staticmethod
    def _execute_influxdb_rest_api(query: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute InfluxDB query using REST API - MORE RELIABLE"""
        try:
            print("🌐 Executing InfluxDB query via REST API...")
            
            # Extract connection parameters
            url = connection_config.get('url', 'http://localhost:8086').rstrip('/')
            token = connection_config.get('token')
            org = connection_config.get('org', 'primary')
            
            # Prepare REST API request
            query_url = f"{url}/api/v2/query"
            headers = {
                'Authorization': f'Token {token}',
                'Accept': 'application/csv',
                'Content-Type': 'application/vnd.flux'
            }
            
            params = {'org': org}
            
            print(f"🔗 REST API URL: {query_url}")
            print(f"📋 Query length: {(query)} characters")
            
            # Execute query
            response = requests.post(
                query_url,
                headers=headers,
                params=params,
                data=query,
                timeout=30
            )
            
            if response.status_code == 200:
                # Parse CSV response
                try:
                    import io
                    csv_data = response.text
                    
                    if not csv_data.strip():
                        print("📊 Query returned empty result set")
                        return True, [], ""
                    
                    # Parse CSV using pandas
                    df = pd.read_csv(io.StringIO(csv_data))
                    
                    # Convert to list of dictionaries
                    data_rows = df.to_dict('records')
                    
                    # Clean up data rows
                    cleaned_rows = []
                    for row in data_rows:
                        cleaned_row = {}
                        for key, value in row.items():
                            # Skip pandas NaN values
                            if pd.notna(value):
                                cleaned_row[key] = value
                        
                        if cleaned_row:  # Only add non-empty rows
                            cleaned_rows.append(cleaned_row)
                    
                    print(f"✅ REST API query successful: {len(cleaned_rows)} rows returned")
                    return True, cleaned_rows, ""
                    
                except Exception as parse_error:
                    error_msg = f"Failed to parse InfluxDB CSV response: {str(parse_error)}"
                    print(f"❌ Parse Error: {error_msg}")
                    return False, [], error_msg
                    
            else:
                # Handle error responses
                error_msg = f"InfluxDB REST API error (status {response.status_code}): {response.text}"
                print(f"❌ REST API Error: {error_msg}")
                return False, [], error_msg
                
        except Exception as e:
            error_msg = f"InfluxDB REST API request failed: {str(e)}"
            print(f"❌ REST API Request Error: {error_msg}")
            return False, [], error_msg
    
    # =================== PARQUET METHODS (Optimized from second implementation) ===================
    
    @staticmethod
    def _execute_parquet_query(query: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute DuckDB query against Parquet files - OPTIMIZED"""
        try:
            print("🦆 Executing DuckDB/Parquet query...")
            
            conn = duckdb.connect()
            result = conn.execute(query).fetchdf()
            data_rows = result.to_dict('records')
            
            print(f"✅ Parquet query executed successfully: {len(data_rows)} rows returned")
            return True, data_rows, ""
            
        except Exception as e:
            error_msg = f"DuckDB query execution failed: {str(e)}"
            print(f"❌ DuckDB Error: {error_msg}")
            return False, [], error_msg
    
    # =================== SQLITE METHODS (Enhanced from both implementations) ===================
    
    @staticmethod
    def _execute_sqlite_query(query: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute SQLite query - ENHANCED"""
        try:
            print("🗃️ Executing SQLite query...")
            
            # Support both database_path and db_path keys for backward compatibility
            db_path = connection_config.get('database_path') or connection_config.get('db_path', '')
            if not db_path:
                return False, [], "Database path not found in connection config"
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            data_rows = [dict(row) for row in rows]
            conn.close()
            
            print(f"✅ SQLite query executed successfully: {len(data_rows)} rows returned")
            return True, data_rows, ""
            
        except Exception as e:
            error_msg = f"SQLite query execution failed: {str(e)}"
            print(f"❌ SQLite Error: {error_msg}")
            return False, [], error_msg
    
    # =================== OPTIMIZED DATA PROCESSING METHODS ===================
    
    @staticmethod
    def _extract_signal_values_optimized(row: Dict, signal_metadata: List[Dict], 
                                       signal_columns: List[str], signal_data: Dict):
        """
        Optimized signal value extraction with minimal overhead
        COMBINED: Enhanced for all data source types
        """
        for signal_info in signal_metadata:
            # Handle different signal metadata formats
            signal_alias = (signal_info.get('value') or 
                          signal_info.get('signal_value') or 
                          signal_info.get('desc') or 
                          signal_info.get('key') or 
                          'Unknown Signal')
            
            signal_value = None
            
            # Fast path: Try signal alias directly (most common case)
            if signal_alias in row:
                signal_value = row[signal_alias]
            
            # Fallback 1: Try database key
            elif signal_info.get('key') in row:
                signal_value = row[signal_info.get('key')]
            
            # Fallback 2: Smart matching (only if needed)
            else:
                signal_key = signal_info.get('key', '').lower()
                signal_alias_lower = signal_alias.lower()
                
                for col_name in signal_columns:
                    col_lower = col_name.lower()
                    if (signal_alias_lower in col_lower or 
                        col_lower in signal_alias_lower or
                        (signal_key and signal_key in col_lower)):
                        signal_value = row[col_name]
                        break
            
            # Add to signal data
            if signal_alias not in signal_data:
                signal_data[signal_alias] = []
            
            if signal_value is not None:
                try:
                    signal_data[signal_alias].append(float(signal_value))
                except (ValueError, TypeError):
                    signal_data[signal_alias].append(None)
            else:
                signal_data[signal_alias].append(None)
    
    @staticmethod
    def _extract_numeric_values(row: Dict, signal_data: Dict):
        """
        Extract all numeric values when no signal metadata available
        """
        excluded_cols = {'timestamp', '_time', 't_sampling_time', 'bucket_time', 'time'}
        
        for key, value in row.items():
            if key not in excluded_cols and value is not None:
                try:
                    numeric_value = float(value)
                    if key not in signal_data:
                        signal_data[key] = []
                    signal_data[key].append(numeric_value)
                except (ValueError, TypeError):
                    continue
    
    @staticmethod
    def _create_datasets(signal_data: Dict, label_count: int) -> List[Dict]:
        """
        Create chart datasets with optimized color assignment
        COMBINED: Enhanced styling for professional appearance
        """
        datasets = []
        colors = [
            '#2196F3', '#4CAF50', '#FF9800', '#9C27B0', 
            '#F44336', '#00BCD4', '#FFEB3B', '#795548',
            '#607D8B', '#E91E63', '#009688', '#FF5722'
        ]
        
        for idx, (signal_alias, values) in enumerate(signal_data.items()):
            # Ensure values match label count
            if len(values) != label_count:
                values = values[:label_count]
                # Pad with None if needed
                while len(values) < label_count:
                    values.append(None)
            
            color = colors[idx % len(colors)]
            
            dataset = {
                "label": signal_alias,
                "data": values,
                "borderColor": color,
                "backgroundColor": f"{color}20",  # Add transparency
                "fill": False,
                "tension": 0.1,
                "pointRadius": 2,
                "pointHoverRadius": 4,
                "borderWidth": 2,
                "signal_key": signal_alias,
                "unit": ""  # Can be enhanced with actual units
            }
            datasets.append(dataset)
        
        return datasets
    
    # =================== TIMESTAMP PROCESSING METHODS ===================
    
    @staticmethod
    def _sort_data_by_timestamp(data_rows: List[Dict]) -> List[Dict]:
        """
        Optimized timestamp sorting with efficient key detection
        COMBINED: Handles multiple timestamp formats from all data sources
        """
        if not data_rows:
            return data_rows
        
        # Find timestamp column efficiently
        first_row = data_rows[0]
        timestamp_col = None
        
        # Priority order: InfluxDB (_time) > SQLite/Parquet (timestamp, t_sampling_time) > Generic (time)
        for col in ['_time', 'timestamp', 't_sampling_time', 'bucket_time', 'time']:
            if col in first_row:
                timestamp_col = col
                break
        
        if not timestamp_col:
            print(f"⚠️ No timestamp column found in: {list(first_row.keys())}")
            return data_rows
        
        # Optimized sort function
        def get_sort_key(row):
            ts_val = row.get(timestamp_col)
            if ts_val is None:
                return datetime.min
            if isinstance(ts_val, datetime):
                return ts_val
            # Fast path for pandas timestamps
            if hasattr(ts_val, 'to_pydatetime'):
                return ts_val.to_pydatetime()
            # String parsing fallback
            if isinstance(ts_val, str):
                try:
                    # Handle InfluxDB RFC3339 format
                    if 'T' in ts_val and ('Z' in ts_val or '+' in ts_val or ts_val.endswith('00')):
                        return datetime.fromisoformat(ts_val.replace('Z', '+00:00'))
                    elif ':' in ts_val:
                        # Time-only format (legacy support)
                        today = datetime.now().date()
                        time_parts = ts_val.split(':')
                        hour, minute = int(time_parts[0]), int(time_parts[1])
                        second = int(time_parts[2]) if len(time_parts) > 2 else 0
                        return datetime.combine(today, datetime.min.time().replace(
                            hour=hour, minute=minute, second=second
                        ))
                    else:
                        return datetime.fromisoformat(ts_val)
                except:
                    return datetime.min
            return datetime.min
        
        return sorted(data_rows, key=get_sort_key)
    
    @staticmethod
    def _extract_timestamp(row: Dict) -> Optional[datetime]:
        """
        Extract timestamp and return as datetime object for ISO conversion
        COMBINED: Handles all timestamp formats from all data sources
        """
        # Priority order: InfluxDB (_time) > SQLite/Parquet (timestamp, t_sampling_time) > Generic
        for col in ['_time', 'timestamp', 't_sampling_time', 'bucket_time', 'time']:
            if col in row and row[col] is not None:
                ts_val = row[col]
                
                # Return datetime objects directly
                if isinstance(ts_val, datetime):
                    return ts_val
                    
                # Fast path for pandas timestamps - convert to datetime
                if hasattr(ts_val, 'to_pydatetime'):
                    return ts_val.to_pydatetime()
                
                # String parsing to datetime
                if isinstance(ts_val, str):
                    try:
                        # Handle InfluxDB RFC3339 format
                        if 'T' in ts_val and ('Z' in ts_val or '+' in ts_val or ts_val.endswith('00')):
                            return datetime.fromisoformat(ts_val.replace('Z', '+00:00'))
                        elif ':' in ts_val:
                            # For time-only strings, use current date as base
                            today = datetime.now().date()
                            time_parts = ts_val.split(':')
                            hour, minute = int(time_parts[0]), int(time_parts[1])
                            second = int(time_parts[2]) if len(time_parts) > 2 else 0
                            return datetime.combine(today, datetime.min.time().replace(
                                hour=hour, minute=minute, second=second
                            ))
                        else:
                            return datetime.fromisoformat(ts_val)
                    except:
                        continue
        return None
    
    @staticmethod
    def _calculate_time_range_iso(sorted_data_rows: List[Dict]) -> Optional[Dict]:
        """
        Calculate time range with ISO formatted timestamps for Chart.js
        COMBINED: Works with all data source timestamp formats
        """
        if not sorted_data_rows:
            return None
        
        first_timestamp = DataRetrievalService._extract_timestamp(sorted_data_rows[0])
        last_timestamp = DataRetrievalService._extract_timestamp(sorted_data_rows[-1])
        
        if first_timestamp and last_timestamp:
            return {
                "start": first_timestamp.isoformat(),  # ISO format for Chart.js
                "end": last_timestamp.isoformat(),     # ISO format for Chart.js
                "duration_minutes": (last_timestamp - first_timestamp).total_seconds() / 60
            }
        return None
    
    # =================== METADATA AND UTILITY METHODS ===================
    
    @staticmethod
    def _get_signal_metadata_from_db(signal_ids: List[int]) -> List[Dict]:
        """
        Get signal metadata from database - optimized with batch query
        COMBINED: Enhanced error handling and fallback support
        """
        try:
            signal_metadata = []
            db = next(get_db())
            
            # Batch query for efficiency
            signals = db.query(EquipmentSignal).filter(
                EquipmentSignal.id.in_(signal_ids)
            ).all()
            
            for signal in signals:
                signal_metadata.append({
                    'signal_id': signal.id,
                    'id': signal.id,
                    'key': signal.key,
                    'value': signal.value,
                    'desc': signal.desc,
                    'unit': signal.unit,
                    'equipment_id': signal.eqp_id
                })
            
            db.close()
            print(f"📊 Retrieved metadata for {len(signal_metadata)} signals")
            return signal_metadata
            
        except Exception as e:
            print(f"⚠️ Could not fetch signal metadata: {str(e)}")
            # Minimal fallback for common signal names
            return [
                {'key': 'soc', 'value': 'soc', 'desc': 'State of Charge', 'unit': '%'},
                {'key': 'voltage', 'value': 'voltage', 'desc': 'Voltage', 'unit': 'V'},
                {'key': 'current', 'value': 'current', 'desc': 'Current', 'unit': 'A'}
            ]
    
    # =================== MAIN SERVICE METHODS ===================
    
    @staticmethod
    def get_widget_data_with_window_period(db: Session, widget_id: str, time_range: Dict, 
                                          window_period: str = "auto", connection_id: str = None) -> Tuple[bool, Dict, str]:
        """
        Complete widget data retrieval pipeline with Chart.js optimized timestamps
        COMBINED: Enhanced for all data source types with comprehensive error handling
        """
        try:
            print(f"🎯 Retrieving widget data: {widget_id}")
            
            # Get widget configuration
            widget = get_widget_by_id(db, widget_id)
            if not widget:
                return False, {}, "Widget not found"
            
            widget_config = widget_to_dict(widget)
            print(f"📋 Widget config loaded: {widget_config.get('widget_label', 'Unknown')}")
            
            # Validate widget metadata
            is_valid, errors = QueryGenerationService.validate_widget_metadata(db, widget_config)
            if not is_valid:
                error_msg = f"Widget validation errors: {'; '.join(errors)}"
                print(f"❌ Validation failed: {error_msg}")
                return False, {}, error_msg
            
            # Generate query with window period
            success, query, data_source_type, connection_config, window_info = QueryGenerationService.generate_widget_query(
                db, widget_config, time_range, window_period, connection_id
            )
            
            if not success:
                error_msg = f"Query generation failed: {query}"
                print(f"❌ Query generation failed: {error_msg}")
                return False, {}, error_msg
            
            print(f"✅ Query generated for {data_source_type}")
            
            # Execute query
            success, data_rows, error_msg = DataRetrievalService.execute_widget_query(
                query, data_source_type, connection_config
            )
            
            if not success:
                error_msg = f"Query execution failed: {error_msg}"
                print(f"❌ Query execution failed: {error_msg}")
                return False, {}, error_msg
            
            # Format data for Chart.js with proper ISO timestamps
            formatted_data = DataRetrievalService.format_data_for_chart(data_rows, widget_config)
            
            # Add metadata
            formatted_data.update({
                "widget_info": {
                    "widget_id": widget_id,
                    "widget_label": widget_config.get('widget_label'),
                    "widget_type": widget_config.get('widget_type'),
                    "query_executed": query,
                    "data_source_type": data_source_type
                },
                "window_info": window_info,
                "retrieval_timestamp": datetime.now().isoformat()
            })
            
            print(f"🎉 Widget data retrieval completed successfully!")
            return True, formatted_data, ""
            
        except Exception as e:
            error_msg = f"Widget data retrieval failed: {str(e)}"
            print(f"💥 Exception: {error_msg}")
            return False, {}, error_msg
    
    @staticmethod
    def validate_time_range(time_range: Dict) -> Tuple[bool, str]:
        """Validate time range parameters - ENHANCED"""
        try:
            start = time_range.get('start')
            end = time_range.get('end')
            
            if not start or not end:
                return False, "Both start and end time are required"
            
            try:
                start_dt = pd.to_datetime(start)
                end_dt = pd.to_datetime(end)
            except:
                return False, "Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            
            if start_dt >= end_dt:
                return False, "Start time must be before end time"
            
            # Check if time range is reasonable (not too large)
            duration = end_dt - start_dt
            if duration.days > 365:
                return False, "Time range cannot exceed 1 year"
            
            return True, "Time range is valid"
            
        except Exception as e:
            return False