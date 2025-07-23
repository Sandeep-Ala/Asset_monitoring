# services/data_retrieval_service.py - Enhanced InfluxDB v2 Integration

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
    """
    
    @staticmethod
    def format_data_for_chart(data_rows: List[Dict], widget_config: Dict) -> Dict:
        """
        Format database query results for Chart.js with proper ISO timestamps
        Enhanced for InfluxDB data compatibility
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
            
            # Sort data by timestamp first
            sorted_data_rows = DataRetrievalService._sort_data_by_timestamp(data_rows)
            
            # Initialize data structures
            labels = []
            signal_data = {}
            
            # Get signal configuration
            signal_ids = widget_config.get('signal_ids', [])
            
            # Get signal metadata if needed
            if signal_ids and isinstance(signal_ids[0], int):
                signal_metadata = DataRetrievalService._get_signal_metadata_from_db(signal_ids)
            else:
                signal_metadata = signal_ids
            
            print(f"📡 Processing {len(signal_metadata)} signals...")
            
            # Process each data row
            for row in sorted_data_rows:
                # Extract timestamp - handle different timestamp column names
                timestamp = None
                for timestamp_col in ['timestamp', '_time', 't_sampling_time', 'bucket_time', 'time']:
                    if timestamp_col in row and row[timestamp_col]:
                        timestamp = row[timestamp_col]
                        break
                
                if not timestamp:
                    print(f"⚠️ Skipping row without timestamp: {list(row.keys())}")
                    continue
                
                # Convert timestamp to ISO format if needed
                if isinstance(timestamp, str):
                    try:
                        # Handle InfluxDB RFC3339 format
                        if 'T' in timestamp and ('Z' in timestamp or '+' in timestamp or timestamp.endswith('00')):
                            # Already in ISO format or RFC3339
                            iso_timestamp = timestamp.replace('Z', '+00:00') if timestamp.endswith('Z') else timestamp
                        else:
                            # Parse and convert to ISO
                            dt = pd.to_datetime(timestamp)
                            iso_timestamp = dt.isoformat()
                    except:
                        print(f"⚠️ Could not parse timestamp: {timestamp}")
                        continue
                elif hasattr(timestamp, 'isoformat'):
                    # datetime object
                    iso_timestamp = timestamp.isoformat()
                else:
                    print(f"⚠️ Unknown timestamp format: {type(timestamp)} - {timestamp}")
                    continue
                
                labels.append(iso_timestamp)
                
                # Process signal values
                for signal in signal_metadata:
                    signal_key = signal.get('key', signal.get('id', ''))
                    if not signal_key:
                        continue
                    
                    # Initialize signal data if not exists
                    if signal_key not in signal_data:
                        signal_data[signal_key] = {
                            "data": [],
                            "label": signal.get('desc', signal_key),
                            "unit": signal.get('unit', ''),
                            "signal_id": signal.get('id', '')
                        }
                    
                    # Get signal value from row
                    signal_value = row.get(signal_key)
                    
                    # Handle different value types
                    if signal_value is not None:
                        try:
                            # Convert to float for Chart.js
                            if isinstance(signal_value, (int, float)):
                                numeric_value = float(signal_value)
                            elif isinstance(signal_value, str):
                                # Try to parse string numbers
                                numeric_value = float(signal_value) if signal_value.strip() else None
                            else:
                                numeric_value = None
                        except (ValueError, TypeError):
                            numeric_value = None
                    else:
                        numeric_value = None
                    
                    signal_data[signal_key]["data"].append(numeric_value)
            
            # Build datasets for Chart.js
            datasets = []
            colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
            
            for idx, (signal_key, signal_info) in enumerate(signal_data.items()):
                color = colors[idx % len(colors)]
                
                dataset = {
                    "label": f"{signal_info['label']} ({signal_info['unit']})" if signal_info['unit'] else signal_info['label'],
                    "data": signal_info["data"],
                    "borderColor": color,
                    "backgroundColor": color + '20',  # Add transparency
                    "fill": False,
                    "tension": 0.1,
                    "pointRadius": 2,
                    "pointHoverRadius": 4,
                    "signal_key": signal_key,
                    "signal_id": signal_info["signal_id"],
                    "unit": signal_info["unit"]
                }
                datasets.append(dataset)
            
            # Calculate time range
            time_range = None
            if labels:
                time_range = {
                    "start": labels[0],
                    "end": labels[-1],
                    "duration_minutes": DataRetrievalService._calculate_duration_minutes(labels[0], labels[-1])
                }
            
            result = {
                "labels": labels,
                "datasets": datasets,
                "isEmpty": len(labels) == 0,
                "totalPoints": len(labels),
                "timeRange": time_range,
                "signalCount": len(datasets),
                "formatTimestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Chart.js formatting completed: {len(labels)} points, {len(datasets)} datasets")
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
            
            if data_source_type.lower() == "sqlite3":
                return DataRetrievalService._execute_sqlite_query(query, connection_config)
            elif data_source_type.lower() == "parquet":
                return DataRetrievalService._execute_parquet_query(query, connection_config)
            elif data_source_type.lower() == "influxdb":
                return DataRetrievalService._execute_influxdb_query(query, connection_config)
            else:
                return False, [], f"Unsupported data source type: {data_source_type}"
                
        except Exception as e:
            return False, [], f"Query execution error: {str(e)}"
    
    @staticmethod
    def _execute_influxdb_query(query: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute InfluxDB v2 Flux query - ENHANCED VERSION"""
        
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
            print(f"📋 Query length: {len(query)} characters")
            
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
    
    @staticmethod
    def _execute_parquet_query(query: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute DuckDB query against Parquet files - PRESERVED ORIGINAL"""
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
    
    @staticmethod
    def _execute_sqlite_query(query: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute SQLite query - PRESERVED ORIGINAL"""
        try:
            print("🗃️ Executing SQLite query...")
            
            db_path = connection_config.get('database_path', '')
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
    
    @staticmethod
    def get_widget_data_with_window_period(db: Session, widget_id: str, time_range: Dict, 
                                          window_period: str = "auto", connection_id: str = None) -> Tuple[bool, Dict, str]:
        """
        Complete widget data retrieval pipeline with Chart.js optimized timestamps - ENHANCED
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
    
    # HELPER METHODS - ENHANCED FOR INFLUXDB
    
    @staticmethod
    def _sort_data_by_timestamp(data_rows: List[Dict]) -> List[Dict]:
        """Sort data rows by timestamp - handles multiple timestamp column names"""
        try:
            if not data_rows:
                return []
            
            # Find timestamp column
            timestamp_col = None
            timestamp_columns = ['timestamp', '_time', 't_sampling_time', 'bucket_time', 'time']
            
            for col in timestamp_columns:
                if col in data_rows[0]:
                    timestamp_col = col
                    break
            
            if timestamp_col:
                return sorted(data_rows, key=lambda x: pd.to_datetime(x[timestamp_col]))
            else:
                print(f"⚠️ No timestamp column found in: {list(data_rows[0].keys())}")
                return data_rows
                
        except Exception as e:
            print(f"⚠️ Could not sort data by timestamp: {str(e)}")
            return data_rows
    
    @staticmethod
    def _calculate_duration_minutes(start_time: str, end_time: str) -> float:
        """Calculate duration in minutes between two timestamps"""
        try:
            start_dt = pd.to_datetime(start_time)
            end_dt = pd.to_datetime(end_time)
            duration = end_dt - start_dt
            return duration.total_seconds() / 60
        except:
            return 0.0
    
    @staticmethod
    def _get_signal_metadata_from_db(signal_ids: List[int]) -> List[Dict]:
        """Get signal metadata from database"""
        try:
            db = next(get_db())
            metadata = []
            for signal_id in signal_ids:
                signal = db.query(EquipmentSignal).filter(EquipmentSignal.id == signal_id).first()
                if signal:
                    metadata.append({
                        "id": signal.id,
                        "key": signal.key,
                        "value": signal.value,
                        "unit": signal.unit,
                        "desc": signal.desc
                    })
            return metadata
        except Exception as e:
            print(f"⚠️ Could not fetch signal metadata: {str(e)}")
            return []
    
    @staticmethod
    def validate_time_range(time_range: Dict) -> Tuple[bool, str]:
        """Validate time range parameters - PRESERVED ORIGINAL"""
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
            return False, f"Time range validation error: {str(e)}"