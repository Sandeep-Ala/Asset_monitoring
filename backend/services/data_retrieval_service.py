# services/data_retrieval_service.py - Updated with InfluxDB v2 Support

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
    INFLUXDB_AVAILABLE = True
except ImportError:
    INFLUXDB_AVAILABLE = False
    InfluxDBClient = None
    QueryApi = None
    ApiException = Exception

class DataRetrievalService:
    """
    Service for widget data retrieval with Chart.js compatible timestamps
    Supports SQLite, Parquet, and InfluxDB v2 data sources
    """
    
    @staticmethod
    def format_data_for_chart(data_rows: List[Dict], widget_config: Dict) -> Dict:
        """
        Format database query results for Chart.js with proper ISO timestamps
        
        KEY IMPROVEMENT: Sends full ISO timestamps instead of time-only strings
        This eliminates complex frontend processing and ensures proper Chart.js compatibility
        """
        try:
            if not data_rows:
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
            
            # Pre-compute available signal columns for efficiency
            available_columns = list(sorted_data_rows[0].keys()) if sorted_data_rows else []
            signal_columns = [col for col in available_columns 
                            if col not in ['timestamp', 't_sampling_time', 'bucket_time', 'time', '_time']]
            
            # Process each row
            for row in sorted_data_rows:
                # Extract timestamp (handle different column names)
                timestamp = (row.get('timestamp') or 
                           row.get('_time') or 
                           row.get('t_sampling_time') or 
                           row.get('bucket_time') or 
                           row.get('time'))
                
                if timestamp:
                    # Ensure timestamp is in ISO format for Chart.js
                    if isinstance(timestamp, str):
                        # Already a string, ensure it's properly formatted
                        try:
                            # Parse and reformat to ensure ISO compliance
                            parsed_time = pd.to_datetime(timestamp)
                            iso_timestamp = parsed_time.isoformat()
                        except:
                            iso_timestamp = timestamp
                    else:
                        # Convert datetime object to ISO string
                        iso_timestamp = pd.to_datetime(timestamp).isoformat()
                    
                    labels.append(iso_timestamp)
                    
                    # Extract signal values
                    for col in signal_columns:
                        if col not in signal_data:
                            signal_data[col] = []
                        
                        value = row.get(col)
                        # Handle None/null values
                        if value is None:
                            signal_data[col].append(None)
                        else:
                            try:
                                # Convert to float for Chart.js
                                signal_data[col].append(float(value))
                            except (ValueError, TypeError):
                                signal_data[col].append(None)
            
            # Create datasets for Chart.js
            datasets = []
            for i, (signal_key, values) in enumerate(signal_data.items()):
                # Find signal metadata for proper labeling
                signal_label = signal_key
                signal_unit = ""
                
                if signal_metadata:
                    for signal_meta in signal_metadata:
                        if (signal_meta.get('key') == signal_key or 
                            signal_meta.get('value') == signal_key):
                            signal_label = signal_meta.get('desc') or signal_meta.get('value') or signal_key
                            signal_unit = signal_meta.get('unit', "")
                            break
                
                # Add unit to label if available
                if signal_unit:
                    signal_label = f"{signal_label} ({signal_unit})"
                
                datasets.append({
                    "label": signal_label,
                    "data": values,
                    "unit": signal_unit,
                    "signal_key": signal_key
                })
            
            # Calculate time range
            time_range = None
            if labels:
                time_range = {
                    "start": labels[0],
                    "end": labels[-1],
                    "duration_minutes": DataRetrievalService._calculate_duration_minutes(labels[0], labels[-1])
                }
            
            return {
                "labels": labels,
                "datasets": datasets,
                "isEmpty": False,
                "totalPoints": len(labels),
                "timeRange": time_range
            }
            
        except Exception as e:
            print(f"❌ Error formatting data for chart: {str(e)}")
            return {
                "labels": [],
                "datasets": [],
                "isEmpty": True,
                "totalPoints": 0,
                "error": str(e)
            }
    
    @staticmethod
    def _sort_data_by_timestamp(data_rows: List[Dict]) -> List[Dict]:
        """Sort data by timestamp column"""
        try:
            # Find timestamp column
            timestamp_col = None
            if data_rows:
                for col in ['timestamp', '_time', 't_sampling_time', 'bucket_time', 'time']:
                    if col in data_rows[0]:
                        timestamp_col = col
                        break
            
            if timestamp_col:
                return sorted(data_rows, key=lambda x: pd.to_datetime(x[timestamp_col]))
            else:
                return data_rows
        except:
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
        except:
            return []
    
    @staticmethod
    def execute_widget_query(query: str, data_source_type: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute query based on data source type and return results"""
        try:
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
        """Execute InfluxDB v2 Flux query"""
        
        if not INFLUXDB_AVAILABLE:
            return False, [], "InfluxDB client library not installed"
        
        try:
            # Extract connection parameters
            url = connection_config.get('url', 'http://localhost:8086')
            token = connection_config.get('token')
            org = connection_config.get('org', 'primary')
            
            if not token:
                return False, [], "InfluxDB token not found in connection config"
            
            with InfluxDBClient(url=url, token=token, org=org, timeout=30_000) as client:
                query_api = client.query_api()
                
                try:
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
                    
                    return True, data_rows, ""
                    
                except ApiException as e:
                    if e.status == 400:
                        return False, [], f"Invalid Flux query: {str(e)}"
                    elif e.status == 403:
                        return False, [], "Insufficient permissions to query InfluxDB"
                    else:
                        return False, [], f"InfluxDB API error: {str(e)}"
                except Exception as e:
                    return False, [], f"InfluxDB query execution failed: {str(e)}"
                    
        except Exception as e:
            return False, [], f"InfluxDB connection error: {str(e)}"
    
    @staticmethod
    def _execute_parquet_query(query: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute DuckDB query against Parquet files"""
        try:
            conn = duckdb.connect()
            result = conn.execute(query).fetchdf()
            data_rows = result.to_dict('records')
            return True, data_rows, ""
        except Exception as e:
            return False, [], f"DuckDB query execution failed: {str(e)}"
    
    @staticmethod
    def _execute_sqlite_query(query: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute SQLite query"""
        try:
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
            
            return True, data_rows, ""
        except Exception as e:
            return False, [], f"SQLite query execution failed: {str(e)}"
    
    @staticmethod
    def get_widget_data_with_window_period(db: Session, widget_id: str, time_range: Dict, 
                                          window_period: str = "auto", connection_id: str = None) -> Tuple[bool, Dict, str]:
        """
        Complete widget data retrieval pipeline with Chart.js optimized timestamps
        """
        try:
            # Get widget configuration
            widget = get_widget_by_id(db, widget_id)
            if not widget:
                return False, {}, "Widget not found"
            
            widget_config = widget_to_dict(widget)
            
            # Validate widget metadata
            is_valid, errors = QueryGenerationService.validate_widget_metadata(db, widget_config)
            if not is_valid:
                return False, {}, f"Widget validation errors: {'; '.join(errors)}"
            
            # Generate query with window period
            success, query, data_source_type, connection_config, window_info = QueryGenerationService.generate_widget_query(
                db, widget_config, time_range, window_period, connection_id
            )
            
            if not success:
                return False, {}, f"Query generation failed: {query}"
            
            # Execute query
            success, data_rows, error_msg = DataRetrievalService.execute_widget_query(
                query, data_source_type, connection_config
            )
            
            if not success:
                return False, {}, f"Query execution failed: {error_msg}"
            
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
                "window_info": window_info
            })
            
            return True, formatted_data, ""
            
        except Exception as e:
            return False, {}, f"Widget data retrieval failed: {str(e)}"
        
    @staticmethod
    def validate_time_range(time_range: Dict) -> Tuple[bool, str]:
        """Validate time range parameters"""
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