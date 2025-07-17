# services/data_retrieval_service.py - OPTIMIZED WITH PROPER CHART.JS TIMESTAMPS
# Sends ISO formatted timestamps that Chart.js can directly parse

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
class DataRetrievalService:
    """
    Optimized service for widget data retrieval with Chart.js compatible timestamps
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
                            if col not in ['timestamp', 't_sampling_time', 'bucket_time', 'time']]
            
            # Process each data row
            for row in sorted_data_rows:
                # CRITICAL IMPROVEMENT: Extract and send full ISO timestamp
                timestamp = DataRetrievalService._extract_timestamp(row)
                if timestamp:
                    # Send ISO format timestamp that Chart.js can directly parse
                    iso_timestamp = timestamp.isoformat()
                    labels.append(iso_timestamp)
                    
                    # Extract signal values efficiently
                    if signal_metadata:
                        DataRetrievalService._extract_signal_values_optimized(
                            row, signal_metadata, signal_columns, signal_data
                        )
                    else:
                        # Fallback: extract all numeric columns
                        DataRetrievalService._extract_numeric_values(row, signal_data)
            
            # Create datasets
            datasets = DataRetrievalService._create_datasets(signal_data, len(labels))
            
            # Calculate time range with full ISO timestamps
            time_range = DataRetrievalService._calculate_time_range_iso(sorted_data_rows)
            
            result = {
                "labels": labels,  # Now contains ISO timestamps like "2025-03-01T07:50:00"
                "datasets": datasets,
                "isEmpty": False,
                "totalPoints": len(labels),
                "timeRange": time_range,
                "actual_points": len(labels)
            }
            
            # Add debug info for first few timestamps
            if len(labels) > 0:
                print(f" Chart data formatted with ISO timestamps:")
                print(f"   - Total points: {len(labels)}")
                print(f"   - First timestamp: {labels[0]}")
                print(f"   - Last timestamp: {labels[-1]}")
                print(f"   - Sample values: {datasets[0]['data'][:3] if datasets and datasets[0]['data'] else []}")
            
            return result
            
        except Exception as e:
            print(f" Error formatting chart data: {str(e)}")
            return {
                "labels": [],
                "datasets": [],
                "isEmpty": True,
                "totalPoints": 0,
                "timeRange": None,
                "error": str(e)
            }
    
    @staticmethod
    def _extract_signal_values_optimized(row: Dict, signal_metadata: List[Dict], 
                                       signal_columns: List[str], signal_data: Dict):
        """
        Optimized signal value extraction with minimal overhead
        """
        for signal_info in signal_metadata:
            signal_alias = signal_info.get('value', signal_info.get('signal_value', 'Unknown Signal'))
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
        excluded_cols = {'timestamp', 't_sampling_time', 'bucket_time', 'time'}
        
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
        """
        datasets = []
        colors = [
            "#2196F3", "#4CAF50", "#FF9800", "#9C27B0", 
            "#F44336", "#00BCD4", "#FFEB3B", "#795548"
        ]
        
        for idx, (signal_alias, values) in enumerate(signal_data.items()):
            # Ensure values match label count
            if len(values) != label_count:
                values = values[:label_count]
            
            color = colors[idx % len(colors)]
            
            dataset = {
                "label": signal_alias,
                "data": values,
                "borderColor": color,
                "backgroundColor": f"{color}20",
                "borderWidth": 2,
                "fill": False,
                "tension": 0.1,
                "pointRadius": 3,
                "pointHoverRadius": 5
            }
            datasets.append(dataset)
        
        return datasets
    
    @staticmethod
    def _calculate_time_range_iso(sorted_data_rows: List[Dict]) -> Optional[Dict]:
        """
        Calculate time range with ISO formatted timestamps for Chart.js
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
    
    @staticmethod
    def _get_signal_metadata_from_db(signal_ids: List[int]) -> List[Dict]:
        """
        Get signal metadata from database - optimized with minimal logging
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
                    'key': signal.key,
                    'value': signal.value,
                    'unit': signal.unit,
                    'equipment_id': signal.eqp_id
                })
            
            db.close()
            return signal_metadata
            
        except Exception:
            # Minimal fallback
            return [{'key': 'soc', 'value': 'soc', 'column_name': 'soc'}]
    
    @staticmethod
    def _sort_data_by_timestamp(data_rows: List[Dict]) -> List[Dict]:
        """
        Optimized timestamp sorting with efficient key detection
        """
        if not data_rows:
            return data_rows
        
        # Find timestamp column efficiently
        first_row = data_rows[0]
        timestamp_col = None
        
        for col in ['timestamp', 't_sampling_time', 'bucket_time', 'time']:
            if col in first_row:
                timestamp_col = col
                break
        
        if not timestamp_col:
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
                    if 'T' in ts_val or '+' in ts_val:
                        return datetime.fromisoformat(ts_val.replace('Z', '+00:00'))
                    elif ':' in ts_val:
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
        """
        for col in ['timestamp', 't_sampling_time', 'bucket_time', 'time']:
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
                        if 'T' in ts_val or '+' in ts_val:
                            return datetime.fromisoformat(ts_val.replace('Z', '+00:00'))
                        elif ':' in ts_val:
                            # For time-only strings, use current date as base
                            # This maintains the original behavior but now we return full datetime
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
    def execute_widget_query(query: str, data_source_type: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """
        Execute widget query and return results
        """
        try:
            if data_source_type == "sqlite":
                return DataRetrievalService._execute_sqlite_query(query, connection_config)
            elif data_source_type == "parquet":
                return DataRetrievalService._execute_parquet_query(query, connection_config)
            else:
                return False, [], f"Unsupported data source type: {data_source_type}"
        except Exception as e:
            return False, [], f"Query execution error: {str(e)}"
    
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
            
            db_path = connection_config.get('db_path', '')
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
            
            return True, ""
        except Exception as e:
            return False, f"Time range validation error: {str(e)}"

    @staticmethod
    def get_data_source_status(db: Session, connection_id: str = None) -> Dict[str, Any]:
        """Get status of data source connection"""
        try:

            
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
                "connections": [
                    {
                        "id": conn.id,
                        "name": conn.name,
                        "db_type": conn.db_type,
                        "status": conn.status
                    }
                    for conn in connections
                ]
            }
            
            return status_info
        except Exception as e:
            return {"status": "error", "message": f"Status check error: {str(e)}"}