# services/query_generation_service.py - Complete Fixed Implementation with Backward Compatibility

from typing import Dict, List, Tuple, Optional, Any
from sqlalchemy.orm import Session
import services.meta_crud as meta_crud
import services.datasource_crud as datasource_crud
from datetime import datetime, timedelta
import json
from config import WINDOW_PERIOD_OPTIONS
from config import calculate_optimal_window_period, MAX_POINTS_PER_WIDGET

class QueryGenerationService:
    """
    Service to generate database queries from widget metadata
    Supports SQLite, Parquet, and InfluxDB v2 data sources
    
    BACKWARD COMPATIBILITY: All existing parquet/SQLite functionality preserved
    """
    
    @staticmethod
    def generate_widget_query(db: Session, widget_config: Dict, time_range: Dict, 
                            window_period: str = "auto", connection_id: str = None) -> Tuple[bool, str, str, Dict, Dict]:
        """
        Generate query for widget data retrieval with window period support
        
        Returns: (success, query, data_source_type, connection_config, window_info)
        """
        try:
            print(f"🔧 Query Generation Started - Connection ID: {connection_id}")
            
            # Extract widget metadata
            equipment_ids = widget_config.get('equipment_ids', [])
            signal_ids = widget_config.get('signal_ids', [])
            filter_selections = widget_config.get('filter_selections', {})
            
            if not equipment_ids or not signal_ids:
                return False, "Equipment and signals are required", "", {}, {}
            
            print(f"📊 Widget Config - Equipment IDs: {equipment_ids}, Signal IDs: {signal_ids}")
            
            # Calculate optimal window period if auto
            window_info = {}
            if window_period == "auto":
                time_start = time_range.get('start', '')
                time_end = time_range.get('end', '')
                
                window_str, window_seconds, total_points = calculate_optimal_window_period(
                    time_start, time_end, MAX_POINTS_PER_WIDGET
                )
                
                window_info = {
                    "window_period": window_str,
                    "window_seconds": window_seconds,
                    "estimated_points": total_points,
                    "max_points_limit": MAX_POINTS_PER_WIDGET,
                    "auto_calculated": True
                }
                print(f"⏱️ Auto Window: {window_str} ({window_seconds}s), Est. Points: {total_points}")
            else:
                # Use provided window period
                window_seconds = WINDOW_PERIOD_OPTIONS.get(window_period, 3600)
                window_info = {
                    "window_period": window_period,
                    "window_seconds": window_seconds,
                    "auto_calculated": False
                }
                print(f"⏱️ Manual Window: {window_period} ({window_seconds}s)")
            
            # Get equipment metadata
            equipment_info = []
            for eq_id in equipment_ids:
                equipment = meta_crud.get_equipment_by_id(db, eq_id)
                if equipment:
                    # Get model name for equipment
                    model = meta_crud.get_master_model_by_id(db, equipment.model_id)
                    equipment_dict = {
                        "id": equipment.id,
                        "name": equipment.name,
                        "location": equipment.location,
                        "model_name": model.name if model else "unknown",
                        "model_id": equipment.model_id
                    }
                    equipment_info.append(equipment_dict)
                    print(f"🏭 Equipment: {equipment.name} (Model: {model.name if model else 'unknown'})")
            
            # Get signal metadata
            signal_info = []
            for signal_id in signal_ids:
                signal = meta_crud.get_equipment_signal_by_id(db, signal_id)
                if signal:
                    signal_dict = {
                        "id": signal.id,
                        "key": signal.key,
                        "value": signal.value,
                        "unit": signal.unit,
                        "desc": signal.desc,
                        "eqp_id": signal.eqp_id
                    }
                    signal_info.append(signal_dict)
                    print(f"📡 Signal: {signal.key} ({signal.unit}) - {signal.desc}")
            
            # Get data source connection
            if not connection_id:
                # Use first active connection as fallback (preserves existing behavior)
                connections = datasource_crud.get_all_data_connections(db)
                active_connections = [conn for conn in connections if conn.status == 'active']
                if not active_connections:
                    return False, "No active data connections found", "", {}, {}
                connection = active_connections[0]
                connection_id = connection.id
                print(f"🔗 Using default connection: {connection.name}")
            else:
                connection = datasource_crud.get_data_connection_by_id(db, connection_id)
                if not connection:
                    return False, f"Connection {connection_id} not found", "", {}, {}
                print(f"🔗 Using specified connection: {connection.name}")
            
            # Get connection configuration
            connection_config = datasource_crud.get_connection_config_dict(db, connection_id)
            data_source_type = connection.db_type
            print(f"🗄️ Data Source Type: {data_source_type}")
            
            # Generate query based on data source type
            if data_source_type.lower() == 'sqlite3':
                print("🔍 Generating SQLite query...")
                success, query = QueryGenerationService._generate_sqlite_query_with_window(
                    equipment_info, signal_info, filter_selections, time_range, connection_config, window_info
                )
            elif data_source_type.lower() == 'parquet':
                print("🔍 Generating Parquet query...")
                success, query = QueryGenerationService._generate_parquet_query_with_window(
                    equipment_info, signal_info, filter_selections, time_range, connection_config, window_info
                )
            elif data_source_type.lower() == 'influxdb':
                print("🔍 Generating InfluxDB query...")
                success, query = QueryGenerationService._generate_influxdb_query_with_window(
                    equipment_info, signal_info, filter_selections, time_range, connection_config, window_info
                )
            else:
                return False, f"Unsupported data source type: {data_source_type}", "", {}, {}
            
            if success:
                print(f"✅ Query Generated Successfully")
                print(f"📝 Query Preview: {query[:200]}...")
                return True, query, data_source_type, connection_config, window_info
            else:
                print(f"❌ Query Generation Failed: {query}")
                return False, query, data_source_type, connection_config, window_info
                
        except Exception as e:
            error_msg = f"Query generation error: {str(e)}"
            print(f"💥 Exception: {error_msg}")
            return False, error_msg, "", {}, {}
    
    @staticmethod
    def _generate_influxdb_query_with_window(equipment_info: List[Dict], signal_info: List[Dict], 
                                           filter_selections: Dict, time_range: Dict, 
                                           connection_config: Dict, window_info: Dict) -> Tuple[bool, str]:
        """Generate InfluxDB v2 Flux query with window aggregation - ENHANCED VERSION"""
        try:
            print("🏗️ Building InfluxDB Flux query...")
            
            # Extract time range and window
            time_start = time_range.get('start', '')
            time_end = time_range.get('end', '')
            window_seconds = window_info.get('window_seconds', 3600)
            
            if not time_start or not time_end:
                return False, "Time range start and end are required"
            
            # Get bucket from connection config
            bucket = connection_config.get('bucket', '')
            if not bucket:
                return False, "Bucket not found in connection config"
            
            print(f"📦 Using bucket: {bucket}, Window: {window_seconds}s")
            
            # Determine measurement name from equipment metadata
            # Enhanced strategies for measurement name determination:
            measurement_names = set()
            
            if equipment_info:
                for equipment in equipment_info:
                    # Strategy 1: Use model name directly
                    model_name = equipment.get('model_name', '').lower().replace(' ', '_')
                    if model_name and model_name != 'unknown':
                        measurement_names.add(model_name)
                   
                
                print(f"📏 Potential measurements: {list(measurement_names)}")
            else:
                return False, "No equipment specified"
            
            # Build Flux query for InfluxDB v2
            flux_lines = []
            
            # Start with basic from clause
            flux_lines.append(f'from(bucket: "{bucket}")')
            
            # Add time range filter
            flux_lines.append(f'  |> range(start: {time_start}, stop: {time_end})')
            
            # Filter by measurement(s) - use OR for multiple measurements
            if len(measurement_names) == 1:
                measurement_name = list(measurement_names)[0]
                flux_lines.append(f'  |> filter(fn: (r) => r._measurement == "{measurement_name}")')
                print(f"📊 Single measurement filter: {measurement_name}")
            else:
                # Multiple potential measurement names
                measurement_filter_parts = []
                for measurement_name in sorted(measurement_names):
                    measurement_filter_parts.append(f'r._measurement == "{measurement_name}"')
                measurement_filter = ' or '.join(measurement_filter_parts)
                flux_lines.append(f'  |> filter(fn: (r) => {measurement_filter})')
                print(f"📊 Multi-measurement filter: {len(measurement_names)} options")
            
            # Add signal field filters
            if signal_info:
                signal_keys = [signal['key'] for signal in signal_info if signal.get('key')]
                if signal_keys:
                    if len(signal_keys) == 1:
                        flux_lines.append(f'  |> filter(fn: (r) => r._field == "{signal_keys[0]}")')
                        print(f"📡 Single field filter: {signal_keys[0]}")
                    else:
                        signal_filter_parts = []
                        for signal_key in signal_keys:
                            signal_filter_parts.append(f'r._field == "{signal_key}"')
                        signal_filter = ' or '.join(signal_filter_parts)
                        flux_lines.append(f'  |> filter(fn: (r) => {signal_filter})')
                        print(f"📡 Multi-field filter: {signal_keys}")
            
            # Add tag filters from filter_selections
            if filter_selections and isinstance(filter_selections, dict):
                print(f"🏷️ Processing filters: {filter_selections}")
                for equipment_key, filters in filter_selections.items():
                    if isinstance(filters, dict):
                        # Multiple filters for this equipment
                        for filter_key, filter_value in filters.items():
                            # Extract the actual filter name after the number prefix
                            if '_' in filter_key and filter_key.split('_')[0].isdigit():
                                actual_filter_key = '_'.join(filter_key.split('_')[1:])
                            else:
                                actual_filter_key = filter_key
                            
                            if filter_value and str(filter_value).strip():
                                flux_lines.append(f'  |> filter(fn: (r) => r.{actual_filter_key} == "{filter_value}")')
                                print(f"🏷️ Added tag filter: {actual_filter_key} = {filter_value}")
                    
                    elif filters and str(filters).strip():
                        # Single value filter
                        if '_' in equipment_key and equipment_key.split('_')[0].isdigit():
                            actual_filter_key = '_'.join(equipment_key.split('_')[1:])
                        else:
                            actual_filter_key = equipment_key
                        
                        flux_lines.append(f'  |> filter(fn: (r) => r.{actual_filter_key} == "{filters}")')
                        print(f"🏷️ Added tag filter: {actual_filter_key} = {filters}")
            
            # Add window aggregation
            window_duration = f"{round(window_seconds)}s"
            flux_lines.append(f'  |> aggregateWindow(every: {window_duration}, fn: mean, createEmpty: false)')
            
            # Pivot to get fields as columns (required for Chart.js format)
            flux_lines.append('  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")')
            
            # Drop unnecessary columns to clean up output
            flux_lines.append('  |> drop(columns: ["_start", "_stop", "_measurement"])')
            
            # Sort by time
            flux_lines.append('  |> sort(columns: ["_time"])')
            
            # Yield results
            flux_lines.append('  |> yield(name: "mean")')
            
            # Join all lines
            flux_query = '\n'.join(flux_lines)
            
            print("✅ InfluxDB Flux query generated successfully")
            return True, flux_query
            
        except Exception as e:
            error_msg = f"InfluxDB query generation error: {str(e)}"
            print(f"❌ InfluxDB Error: {error_msg}")
            return False, error_msg
    
    @staticmethod
    def _generate_sqlite_query_with_window(equipment_info: List[Dict], signal_info: List[Dict], 
                                          filter_selections: Dict, time_range: Dict, 
                                          connection_config: Dict, window_info: Dict) -> Tuple[bool, str]:
        """Generate SQLite query with time_bucket aggregation - PRESERVED ORIGINAL LOGIC"""
        try:
            print("🏗️ Building SQLite query...")
            
            # Extract time range and window
            time_start = time_range.get('start', '')
            time_end = time_range.get('end', '')
            window_seconds = window_info.get('window_seconds', 3600)
            
            if not time_start or not time_end:
                return False, "Time range start and end are required"
            
            # Build SELECT clause with time_bucket and signal aggregation
            select_columns = [
                f"time_bucket(INTERVAL '{window_seconds} seconds', CAST(t_sampling_time AS TIMESTAMP), TIMESTAMP '{time_start}') AS timestamp"
            ]
            
            signal_keys = []
            for signal in signal_info:
                signal_key = signal['key']
                signal_keys.append(signal_key)
                select_columns.append(f"AVG(CAST({signal_key} AS FLOAT)) AS {signal_key}")
            
            print(f"📊 SQLite signals: {signal_keys}")
            
            # Build FROM clause
            # For SQLite, we typically have a single table per equipment
            if equipment_info:
                table_name = f"{equipment_info[0]['model_name'].lower().replace(' ', '_')}_data"
                print(f"📋 SQLite table: {table_name}")
            else:
                return False, "No equipment specified"
            
            # Build WHERE clause
            where_conditions = [
                f"t_sampling_time >= '{time_start}'",
                f"t_sampling_time <= '{time_end}'"
            ]
            
            # Add filter conditions - PRESERVED ORIGINAL LOGIC
            for equipment_key, filters in filter_selections.items():
                if isinstance(filters, dict):
                    for filter_key, filter_value in filters.items():
                        if filter_value:
                            where_conditions.append(f"{filter_key} = '{filter_value}'")
                            print(f"🏷️ SQLite filter: {filter_key} = {filter_value}")
                else:
                    if filters:
                        where_conditions.append(f"{equipment_key} = '{filters}'")
                        print(f"🏷️ SQLite filter: {equipment_key} = {filters}")
            
            # Build GROUP BY clause
            group_by_clause = f"time_bucket(INTERVAL '{window_seconds} seconds', CAST(t_sampling_time AS TIMESTAMP), TIMESTAMP '{time_start}')"
            
            # Combine query parts
            query = f"""
            SELECT {', '.join(select_columns)}
            FROM {table_name}
            WHERE {' AND '.join(where_conditions)}
            GROUP BY {group_by_clause}
            ORDER BY timestamp
            """
            
            print("✅ SQLite query generated successfully")
            return True, query.strip()
            
        except Exception as e:
            error_msg = f"SQLite query generation error: {str(e)}"
            print(f"❌ SQLite Error: {error_msg}")
            return False, error_msg
    
    @staticmethod
    def _generate_parquet_query_with_window(equipment_info: List[Dict], signal_info: List[Dict], 
                                           filter_selections: Dict, time_range: Dict, 
                                           connection_config: Dict, window_info: Dict) -> Tuple[bool, str]:
        """Generate DuckDB query for Parquet files with window aggregation - PRESERVED ORIGINAL LOGIC"""
        try:
            print("🏗️ Building Parquet/DuckDB query...")
            
            # Extract time range and window
            time_start = time_range.get('start', '')
            time_end = time_range.get('end', '')
            window_seconds = window_info.get('window_seconds', 3600)
            
            if not time_start or not time_end:
                return False, "Time range start and end are required"
            
            # Get file path from connection config
            file_path = connection_config.get('file_path', '')
            if not file_path:
                return False, "File path not found in connection config"
            
            print(f"📂 Parquet file: {file_path}")
            
            # Build SELECT clause with time window aggregation
            select_columns = [
                f"time_bucket(INTERVAL '{window_seconds} seconds', CAST(t_sampling_time AS TIMESTAMP)) AS timestamp"
            ]
            
            signal_keys = []
            for signal in signal_info:
                signal_key = signal['key']
                signal_keys.append(signal_key)
                select_columns.append(f"AVG(CAST({signal_key} AS DOUBLE)) AS {signal_key}")
            
            print(f"📊 Parquet signals: {signal_keys}")
            
            # Build WHERE clause
            where_conditions = [
                f"t_sampling_time >= TIMESTAMP '{time_start}'",
                f"t_sampling_time <= TIMESTAMP '{time_end}'"
            ]
            
            # Add filter conditions - PRESERVED ORIGINAL LOGIC
            for equipment_key, filters in filter_selections.items():
                if isinstance(filters, dict):
                    for filter_key, filter_value in filters.items():
                        if filter_value:
                            where_conditions.append(f"{filter_key} = '{filter_value}'")
                            print(f"🏷️ Parquet filter: {filter_key} = {filter_value}")
                else:
                    if filters:
                        where_conditions.append(f"{equipment_key} = '{filters}'")
                        print(f"🏷️ Parquet filter: {equipment_key} = {filters}")
            
            # Build GROUP BY clause
            group_by_clause = f"time_bucket(INTERVAL '{window_seconds} seconds', CAST(t_sampling_time AS TIMESTAMP))"
            
            # Combine query parts
            query = f"""
            SELECT {', '.join(select_columns)}
            FROM read_parquet('{file_path}')
            WHERE {' AND '.join(where_conditions)}
            GROUP BY {group_by_clause}
            ORDER BY timestamp
            """
            
            print("✅ Parquet query generated successfully")
            return True, query.strip()
            
        except Exception as e:
            error_msg = f"Parquet query generation error: {str(e)}"
            print(f"❌ Parquet Error: {error_msg}")
            return False, error_msg
    
    @staticmethod
    def get_default_time_range(range_type: str = "last_1h") -> Dict[str, str]:
        """Generate default time range based on type - PRESERVED ORIGINAL"""
        now = datetime.now()
        
        if range_type == "last_15m":
            return {
                "start": (now - timedelta(minutes=15)).isoformat(),
                "end": now.isoformat(),
                "range_type": "last_15m"
            }
        elif range_type == "last_1h":
            return {
                "start": (now - timedelta(hours=1)).isoformat(),
                "end": now.isoformat(),
                "range_type": "last_1h"
            }
        elif range_type == "last_6h":
            return {
                "start": (now - timedelta(hours=6)).isoformat(),
                "end": now.isoformat(),
                "range_type": "last_6h"
            }
        elif range_type == "last_24h":
            return {
                "start": (now - timedelta(days=1)).isoformat(),
                "end": now.isoformat(),
                "range_type": "last_24h"
            }
        elif range_type == "last_7d":
            return {
                "start": (now - timedelta(days=7)).isoformat(),
                "end": now.isoformat(),
                "range_type": "last_7d"
            }
        else:
            # Default to last 1 hour
            return {
                "start": (now - timedelta(hours=1)).isoformat(),
                "end": now.isoformat(),
                "range_type": "last_1h"
            }
    
    @staticmethod
    def validate_widget_metadata(db: Session, widget_config: Dict) -> Tuple[bool, List[str]]:
        """Validate widget metadata before query generation - PRESERVED ORIGINAL"""
        errors = []
        
        # Check equipment IDs
        equipment_ids = widget_config.get('equipment_ids', [])
        if not equipment_ids:
            errors.append("At least one equipment must be selected")
        else:
            for eq_id in equipment_ids:
                equipment = meta_crud.get_equipment_by_id(db, eq_id)
                if not equipment:
                    errors.append(f"Equipment ID {eq_id} not found")
        
        # Check signal IDs
        signal_ids = widget_config.get('signal_ids', [])
        if not signal_ids:
            errors.append("At least one signal must be selected")
        else:
            for signal_id in signal_ids:
                signal = meta_crud.get_equipment_signal_by_id(db, signal_id)
                if not signal:
                    errors.append(f"Signal ID {signal_id} not found")
        
        return len(errors) == 0, errors