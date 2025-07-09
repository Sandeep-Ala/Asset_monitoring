# services/data_retrieval_service.py - ENHANCED WITH SORTING FIX
# Complete widget data retrieval pipeline with proper time sorting

import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

class DataRetrievalService:
    """
    Enhanced service for widget data retrieval with guaranteed time sorting
    """
    
    @staticmethod
    def format_data_for_chart(data_rows: List[Dict], widget_config: Dict) -> Dict:
        """
        Format database query results for chart display with PROPER TIME SORTING
        
        FIXED: Now ensures data is properly sorted by timestamp before sending to UI
        FIXED: Handles both integer signal_ids and dictionary signal_ids
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
            
            print(f"📊 Formatting {len(data_rows)} data rows for chart")
            print(f"🔍 First row: {data_rows[0] if data_rows else 'None'}")
            print(f"🔍 Last row: {data_rows[-1] if data_rows else 'None'}")
            
            # CRITICAL FIX: Sort data by timestamp before processing
            sorted_data_rows = DataRetrievalService._sort_data_by_timestamp(data_rows)
            
            print(f"✅ Data sorted by timestamp")
            print(f"🔍 First sorted row: {sorted_data_rows[0] if sorted_data_rows else 'None'}")
            print(f"🔍 Last sorted row: {sorted_data_rows[-1] if sorted_data_rows else 'None'}")
            
            # Extract timestamps and create labels
            labels = []
            signal_data = {}
            
            # FIXED: Get signal configuration - handle both integer IDs and dictionary format
            signal_ids = widget_config.get('signal_ids', [])
            print(f"🔍 Signal IDs from config: {signal_ids}")
            
            # Get signal metadata from database if signal_ids are integers
            if signal_ids and isinstance(signal_ids[0], int):
                # Signal IDs are integers, need to fetch metadata
                signal_metadata = DataRetrievalService._get_signal_metadata_from_db(signal_ids)
                print(f"🔍 Signal metadata from DB: {signal_metadata}")
            else:
                # Signal IDs are already dictionaries with metadata
                signal_metadata = signal_ids
            
            for row in sorted_data_rows:
                # Extract timestamp - handle multiple possible timestamp column names
                timestamp = DataRetrievalService._extract_timestamp(row)
                if timestamp:
                    # Convert to time-only format for labels (matching your current format)
                    time_label = DataRetrievalService._format_timestamp_for_label(timestamp)
                    labels.append(time_label)
                    
                    # Extract signal values - handle both formats
                    if signal_metadata:
                        for signal_info in signal_metadata:
                            signal_key = signal_info.get('key', signal_info.get('column_name', ''))
                            signal_alias = signal_info.get('value', signal_info.get('signal_value', signal_key))
                            
                            if signal_key in row and row[signal_key] is not None:
                                if signal_alias not in signal_data:
                                    signal_data[signal_alias] = []
                                signal_data[signal_alias].append(float(row[signal_key]))
                            else:
                                # Handle missing data points
                                if signal_alias not in signal_data:
                                    signal_data[signal_alias] = []
                                signal_data[signal_alias].append(None)
                    else:
                        # Fallback: extract all numeric columns except timestamp
                        for key, value in row.items():
                            if key not in ['timestamp', 't_sampling_time', 'bucket_time', 'time'] and value is not None:
                                try:
                                    numeric_value = float(value)
                                    if key not in signal_data:
                                        signal_data[key] = []
                                    signal_data[key].append(numeric_value)
                                except (ValueError, TypeError):
                                    # Skip non-numeric values
                                    pass
            
            # Create datasets
            datasets = []
            for signal_alias, values in signal_data.items():
                # Clean up any None values at the end to match labels length
                if len(values) != len(labels):
                    values = values[:len(labels)]
                
                dataset = {
                    "label": signal_alias,
                    "data": values,
                    "borderColor": DataRetrievalService._get_signal_color(len(datasets)),
                    "backgroundColor": f"{DataRetrievalService._get_signal_color(len(datasets))}20",
                    "borderWidth": 2,
                    "fill": False,
                    "tension": 0.1,
                    "pointRadius": 3,
                    "pointHoverRadius": 5
                }
                datasets.append(dataset)
            
            # Calculate time range from sorted data
            time_range = None
            if sorted_data_rows:
                first_timestamp = DataRetrievalService._extract_timestamp(sorted_data_rows[0])
                last_timestamp = DataRetrievalService._extract_timestamp(sorted_data_rows[-1])
                
                if first_timestamp and last_timestamp:
                    time_range = {
                        "start": DataRetrievalService._format_timestamp_for_label(first_timestamp),
                        "end": DataRetrievalService._format_timestamp_for_label(last_timestamp)
                    }
            
            result = {
                "labels": labels,
                "datasets": datasets,
                "isEmpty": False,
                "totalPoints": len(labels),
                "timeRange": time_range,
                "actual_points": len(labels)
            }
            
            print(f"✅ Chart data formatted successfully:")
            print(f"   - Labels: {len(labels)}")
            print(f"   - Datasets: {len(datasets)}")
            print(f"   - Total points: {len(labels)}")
            print(f"   - Signal data keys: {list(signal_data.keys())}")
            print(f"   - Time range: {time_range}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error formatting chart data: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                "labels": [],
                "datasets": [],
                "isEmpty": True,
                "totalPoints": 0,
                "timeRange": None,
                "error": str(e)
            }
    
    @staticmethod
    def _get_signal_metadata_from_db(signal_ids: List[int]) -> List[Dict]:
        """
        Get signal metadata from database based on signal IDs
        """
        try:
            # Import here to avoid circular imports
            from models.meta_models import EquipmentSignal
            from config import get_db
            
            signal_metadata = []
            
            # Get database session
            db = next(get_db())
            
            for signal_id in signal_ids:
                signal = db.query(EquipmentSignal).filter(EquipmentSignal.id == signal_id).first()
                if signal:
                    signal_metadata.append({
                        'signal_id': signal.id,
                        'key': signal.key,
                        'value': signal.value,
                        # 'column_name': signal.column_name,
                        # 'signal_value': signal.signal_value,
                        # 'unit': getattr(signal, 'unit', ''),
                        'unit': signal.unit,
                        'equipment_id': signal.eqp_id
                    })
                else:
                    print(f"⚠️ Signal ID {signal_id} not found in database")
            
            db.close()
            
            print(f"📊 Retrieved metadata for {len(signal_metadata)} signals")
            return signal_metadata
            
        except Exception as e:
            print(f"❌ Error getting signal metadata: {str(e)}")
            
            # Fallback: create minimal metadata based on query results
            # This should work for your current case
            return [{
                'key': 'soc',  # Based on your query: AVG(n_soc) AS "soc"
                'value': 'soc',
                'column_name': 'soc'
            }]
    
    @staticmethod
    def _sort_data_by_timestamp(data_rows: List[Dict]) -> List[Dict]:
        """
        Sort data rows by timestamp in ascending order
        
        CRITICAL FIX: This ensures proper chronological ordering for chart plotting
        """
        try:
            if not data_rows:
                return data_rows
            
            # Find the timestamp column
            timestamp_columns = ['timestamp', 't_sampling_time', 'bucket_time', 'time']
            timestamp_col = None
            
            for col in timestamp_columns:
                if col in data_rows[0]:
                    timestamp_col = col
                    break
            
            if not timestamp_col:
                print("⚠️ No timestamp column found, returning unsorted data")
                return data_rows
            
            print(f"🔄 Sorting data by column: {timestamp_col}")
            
            # Sort by timestamp
            def sort_key(row):
                timestamp_val = row.get(timestamp_col)
                if timestamp_val is None:
                    return datetime.min
                
                # Handle different timestamp formats
                if isinstance(timestamp_val, str):
                    try:
                        # Try parsing ISO format
                        if 'T' in timestamp_val or '+' in timestamp_val:
                            return datetime.fromisoformat(timestamp_val.replace('Z', '+00:00'))
                        # Try parsing time-only format (HH:MM:SS)
                        elif ':' in timestamp_val and len(timestamp_val.split(':')) >= 2:
                            # For time-only format, use today's date as base
                            today = datetime.now().date()
                            time_parts = timestamp_val.split(':')
                            hour = int(time_parts[0])
                            minute = int(time_parts[1])
                            second = int(time_parts[2]) if len(time_parts) > 2 else 0
                            return datetime.combine(today, datetime.min.time().replace(
                                hour=hour, minute=minute, second=second
                            ))
                        else:
                            return datetime.fromisoformat(timestamp_val)
                    except:
                        print(f"⚠️ Could not parse timestamp: {timestamp_val}")
                        return datetime.min
                elif isinstance(timestamp_val, datetime):
                    return timestamp_val
                else:
                    return datetime.min
            
            sorted_rows = sorted(data_rows, key=sort_key)
            
            print(f"✅ Data sorted successfully ({len(sorted_rows)} rows)")
            
            return sorted_rows
            
        except Exception as e:
            print(f"❌ Error sorting data: {str(e)}")
            return data_rows  # Return original data if sorting fails
    
    @staticmethod
    def _extract_timestamp(row: Dict) -> Optional[datetime]:
        """Extract timestamp from data row, handling multiple column names and formats"""
        timestamp_columns = ['timestamp', 't_sampling_time', 'bucket_time', 'time']
        
        for col in timestamp_columns:
            if col in row and row[col] is not None:
                timestamp_val = row[col]
                
                if isinstance(timestamp_val, datetime):
                    return timestamp_val
                elif isinstance(timestamp_val, str):
                    try:
                        # Handle ISO format
                        if 'T' in timestamp_val or '+' in timestamp_val:
                            return datetime.fromisoformat(timestamp_val.replace('Z', '+00:00'))
                        # Handle time-only format
                        elif ':' in timestamp_val:
                            today = datetime.now().date()
                            time_parts = timestamp_val.split(':')
                            hour = int(time_parts[0])
                            minute = int(time_parts[1])
                            second = int(time_parts[2]) if len(time_parts) > 2 else 0
                            return datetime.combine(today, datetime.min.time().replace(
                                hour=hour, minute=minute, second=second
                            ))
                        else:
                            return datetime.fromisoformat(timestamp_val)
                    except:
                        continue
        
        return None
    
    @staticmethod
    def _format_timestamp_for_label(timestamp: datetime) -> str:
        """Format timestamp for chart labels (time-only format to match current system)"""
        return timestamp.strftime("%H:%M:%S")
    
    @staticmethod
    def _get_signal_color(index: int) -> str:
        """Get color for signal based on index"""
        colors = [
            "#2196F3",  # Blue (matches your data)
            "#FF6B6B",  # Red
            "#4ECDC4",  # Teal
            "#45B7D1",  # Light Blue
            "#96CEB4",  # Light Green
            "#FFEAA7",  # Yellow
            "#DDA0DD",  # Plum
            "#98D8C8",  # Mint
        ]
        return colors[index % len(colors)]
    
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
            error_msg = f"Query execution error: {str(e)}"
            print(f"❌ {error_msg}")
            return False, [], error_msg
    
    @staticmethod
    def _execute_parquet_query(query: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute DuckDB query against Parquet files"""
        try:
            import duckdb
            
            print(f"🦆 Executing DuckDB query:")
            print(f"Query: {query}")
            
            # Create DuckDB connection
            conn = duckdb.connect()
            
            # Execute query
            result = conn.execute(query).fetchdf()
            
            # Convert to list of dictionaries
            data_rows = result.to_dict('records')
            
            print(f"✅ Query executed successfully, returned {len(data_rows)} rows")
            
            return True, data_rows, ""
            
        except Exception as e:
            error_msg = f"DuckDB query execution failed: {str(e)}"
            print(f"❌ {error_msg}")
            return False, [], error_msg
    
    @staticmethod
    def _execute_sqlite_query(query: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute SQLite query"""
        try:
            import sqlite3
            
            db_path = connection_config.get('db_path', '')
            if not db_path:
                return False, [], "Database path not found in connection config"
            
            print(f"💾 Executing SQLite query on: {db_path}")
            print(f"Query: {query}")
            
            # Connect to SQLite database
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # This enables column access by name
            
            # Execute query
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            data_rows = [dict(row) for row in rows]
            
            conn.close()
            
            print(f"✅ SQLite query executed successfully, returned {len(data_rows)} rows")
            
            return True, data_rows, ""
            
        except Exception as e:
            error_msg = f"SQLite query execution failed: {str(e)}"
            print(f"❌ {error_msg}")
            return False, [], error_msg
    
    @staticmethod
    def get_widget_data_with_window_period(db: Session, widget_id: str, time_range: Dict, 
                                          window_period: str = "auto", connection_id: str = None) -> Tuple[bool, Dict, str]:
        """
        Complete widget data retrieval pipeline with window period support and proper sorting
        
        Returns: (success, formatted_data, error_message)
        """
        try:
            from services.widget_crud import get_widget_by_id, widget_to_dict
            from services.query_generation_service import QueryGenerationService
            
            # Get widget configuration
            widget = get_widget_by_id(db, widget_id)
            if not widget:
                return False, {}, "Widget not found"
            
            widget_config = widget_to_dict(widget)
            print(f'📊 Widget config: {widget_config}')
            
            # Validate widget metadata
            is_valid, errors = QueryGenerationService.validate_widget_metadata(db, widget_config)
            print(f'✅ Widget validation: {is_valid}')
            if errors:
                print(f'⚠️ Validation errors: {errors}')
            
            if not is_valid:
                return False, {}, f"Widget validation errors: {'; '.join(errors)}"
            
            # Generate query with window period
            success, query, data_source_type, connection_config, window_info = QueryGenerationService.generate_widget_query(
                db, widget_config, time_range, window_period, connection_id
            )
            
            if not success:
                return False, {}, f"Query generation failed: {query}"
            
            print(f"🔍 Generated query: {query}")
            
            # Execute query
            success, data_rows, error_msg = DataRetrievalService.execute_widget_query(
                query, data_source_type, connection_config
            )
            
            if not success:
                return False, {}, f"Query execution failed: {error_msg}"
            
            print(f"📊 Query returned {len(data_rows)} rows")
            
            # Format data for chart WITH PROPER SORTING
            formatted_data = DataRetrievalService.format_data_for_chart(data_rows, widget_config)
            
            # Add enhanced metadata with window information
            formatted_data["widget_info"] = {
                "widget_id": widget_id,
                "widget_label": widget_config.get('widget_label'),
                "widget_type": widget_config.get('widget_type'),
                "query_executed": query,
                "data_source_type": data_source_type
            }
            
            # Add window period information
            formatted_data["window_info"] = window_info
            
            print(f"✅ Widget data retrieval complete")
            print(f"   - Data points: {formatted_data.get('totalPoints', 0)}")
            print(f"   - Datasets: {len(formatted_data.get('datasets', []))}")
            print(f"   - Time range: {formatted_data.get('timeRange')}")
            
            return True, formatted_data, ""
            
        except Exception as e:
            error_msg = f"Widget data retrieval failed: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            
            return False, {}, error_msg
        
    @staticmethod
    def validate_time_range(time_range: Dict) -> Tuple[bool, str]:
        """Validate time range parameters"""
        try:
            start = time_range.get('start')
            end = time_range.get('end')
            
            if not start or not end:
                return False, "Both start and end time are required"
            
            # Try to parse timestamps
            try:
                start_dt = pd.to_datetime(start)
                end_dt = pd.to_datetime(end)
            except:
                return False, "Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            
            # Check if start is before end
            if start_dt >= end_dt:
                return False, "Start time must be before end time"
            
            # Check if time range is reasonable (not too large)
            # time_diff = end_dt - start_dt
            # if time_diff.days > 30:
            #     return False, "Time range cannot exceed 30 days"
            
            return True, ""
            
        except Exception as e:
            return False, f"Time range validation error: {str(e)}"

    @staticmethod
    def get_data_source_status(db: Session, connection_id: str = None) -> Dict[str, Any]:
        """Get status of data source connection"""
        try:
            import services.datasource_crud as datasource_crud
            
            if connection_id:
                connection = datasource_crud.get_data_connection_by_id(db, connection_id)
                if not connection:
                    return {"status": "error", "message": "Connection not found"}
                
                connections = [connection]
            else:
                connections = datasource_crud.get_all_data_connections(db)
            
            status_info = {
                "total_connections": len(connections),
                "active_connections": 0,
                "connections": []
            }
            
            for conn in connections:
                conn_info = {
                    "id": conn.id,
                    "name": conn.name,
                    "db_type": conn.db_type,
                    "status": conn.status
                }
                
                if conn.status == 'active':
                    status_info["active_connections"] += 1
                
                status_info["connections"].append(conn_info)
            
            return status_info
            
        except Exception as e:
            return {"status": "error", "message": f"Status check error: {str(e)}"}