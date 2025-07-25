# services/query_generation_service.py - COMBINED InfluxDB + Parquet + SQLite Implementation
# Complete query generation service supporting all three data source types

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
    
    COMBINED IMPLEMENTATION:
    - InfluxDB v2 Flux query generation with enhanced measurement detection
    - Optimized Parquet/DuckDB queries with cross-platform path handling
    - SQLite queries with time bucket aggregation
    - Backward compatibility with existing functionality
    """
    
    @staticmethod
    def generate_widget_query(db: Session, widget_config: Dict, time_range: Dict, 
                            window_period: str = "auto", connection_id: str = None) -> Tuple[bool, str, str, Dict, Dict]:
        """
        Generate query for widget data retrieval with window period support
        COMBINED: Enhanced for all data source types
        
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
                
                # Calculate estimated points for manual window period
                time_start = time_range.get('start', '')
                time_end = time_range.get('end', '')
                try:
                    start_dt = datetime.fromisoformat(time_start.replace('Z', '+00:00').replace('+00:00', ''))
                    end_dt = datetime.fromisoformat(time_end.replace('Z', '+00:00').replace('+00:00', ''))
                    total_seconds = (end_dt - start_dt).total_seconds()
                    estimated_points = int(total_seconds / window_seconds) if window_seconds > 0 else 100
                except:
                    estimated_points = 100
                
                window_info = {
                    "window_period": window_period,
                    "window_seconds": window_seconds,
                    "estimated_points": estimated_points,
                    "max_points_limit": MAX_POINTS_PER_WIDGET,
                    "auto_calculated": False
                }
                print(f"⏱️ Manual Window: {window_period} ({window_seconds}s), Est. Points: {estimated_points}")
            
            # Get equipment metadata (enhanced)
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
            
            # Get signal metadata (enhanced)
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
                        "eqp_id": signal.eqp_id,
                        "equipment_id": signal.eqp_id  # Backward compatibility
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
            if data_source_type.lower() in ['sqlite3', 'sqlite']:
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
    
    # =================== INFLUXDB QUERY GENERATION ===================
    
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
                flux_lines.append(f'  |> filter(fn: (r) => r["_measurement"] == "{measurement_name}")')
                print(f"📊 Single measurement filter: {measurement_name}")
            else:
                # Multiple potential measurement names
                measurement_filter_parts = []
                for measurement_name in sorted(measurement_names):
                    measurement_filter_parts.append(f'r["_measurement"] == "{measurement_name}"')
                measurement_filter = ' or '.join(measurement_filter_parts)
                flux_lines.append(f'  |> filter(fn: (r) => r["{measurement_filter}"])')
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
    
    # =================== SQLITE QUERY GENERATION ===================
    
    @staticmethod
    def _generate_sqlite_query_with_window(equipment_info: List[Dict], signal_info: List[Dict], 
                                          filter_selections: Dict, time_range: Dict, 
                                          connection_config: Dict, window_info: Dict) -> Tuple[bool, str]:
        """Generate SQLite query with time_bucket aggregation - ENHANCED"""
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
                # Use signal value or key as column alias with AVG aggregation
                signal_alias = signal.get('value') or signal_key
                select_columns.append(f"AVG(CAST({signal_key} AS FLOAT)) AS \"{signal_alias}\"")
            
            print(f"📊 SQLite signals: {signal_keys}")
            
            # Build FROM clause
            # For SQLite, determine table name from equipment info
            if equipment_info:
                # Try multiple table naming strategies
                equipment_name = equipment_info[0]['name'].lower()
                model_name = equipment_info[0]['model_name'].lower().replace(' ', '_')
                
                # Common table naming patterns
                possible_table_names = [
                    f"t_{equipment_name}",  # t_equipment_name
                    f"{model_name}_data",   # model_data
                    f"data_{model_name}",   # data_model
                    equipment_name,         # equipment_name
                    model_name             # model_name
                ]
                
                # Use the first valid table name (could be enhanced with table existence check)
                table_name = possible_table_names[0]
                print(f"📋 SQLite table: {table_name}")
            else:
                return False, "No equipment specified"
            
            # Build WHERE clause
            where_conditions = [
                f"t_sampling_time >= '{time_start}'",
                f"t_sampling_time <= '{time_end}'"
            ]
            
            # Add filter conditions - ENHANCED
            for equipment_key, filters in filter_selections.items():
                if isinstance(filters, dict):
                    for filter_key, filter_value in filters.items():
                        if filter_value and str(filter_value).strip():
                            where_conditions.append(f"{filter_key} = '{filter_value}'")
                            print(f"🏷️ SQLite filter: {filter_key} = {filter_value}")
                else:
                    if filters and str(filters).strip():
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
    
    # =================== PARQUET QUERY GENERATION ===================
    
    @staticmethod
    def _generate_parquet_query_with_window(equipment_info: List[Dict], signal_info: List[Dict], 
                                           filter_selections: Dict, time_range: Dict, 
                                           connection_config: Dict, window_info: Dict) -> Tuple[bool, str]:
        """Generate DuckDB query for Parquet files with window aggregation - OPTIMIZED"""
        try:
            print("🏗️ Building Parquet/DuckDB query...")
            
            # Extract time range and window
            time_start = time_range.get('start', '')
            time_end = time_range.get('end', '')
            window_seconds = window_info.get('window_seconds', 3600)
            
            if not time_start or not time_end:
                return False, "Time range start and end are required"
            
            # Get file path configuration (support both base_path and file_path)
            base_path = connection_config.get('base_path') or connection_config.get('file_path', '')
            if not base_path:
                return False, "Base path or file path not found in connection config"
            
            print(f"📂 Parquet base path: {base_path}")
            
            # Build SELECT clause with time_bucket and signal aggregation
            select_columns = [
                f"time_bucket(INTERVAL '{window_seconds} seconds', CAST(t_sampling_time AS TIMESTAMP), TIMESTAMP '{time_start}') AS timestamp"
            ]
            
            signal_keys = []
            for signal in signal_info:
                signal_key = signal['key']
                signal_keys.append(signal_key)
                # Use signal value or key as column alias with AVG aggregation
                signal_alias = signal.get('value') or signal_key
                select_columns.append(f"AVG(CAST({signal_key} AS DOUBLE)) AS \"{signal_alias}\"")
            
            print(f"📊 Parquet signals: {signal_keys}")
            
            # Build parquet file path pattern
            # ENHANCED: Handle multiple path patterns and cross-platform compatibility
            if equipment_info:
                equipment_name = equipment_info[0]['name'].lower()
                model_name = equipment_info[0]['model_name'].lower()
                
                # Normalize path separators for cross-platform compatibility
                normalized_base_path = base_path.replace('\\', '/')
                
                # Try multiple parquet file patterns
                possible_patterns = [
                    f"{normalized_base_path}/**/equipment={model_name}/dcu=*/*.parquet",  # Hierarchical structure
                    f"{normalized_base_path}/equipment={model_name}/**/*.parquet",        # Alternative structure
                    f"{normalized_base_path}/**/{model_name}*.parquet",                   # Simple pattern
                    f"{normalized_base_path}/*.parquet"                                   # Single file
                ]
                
                # Use the first pattern (could be enhanced with file existence check)
                parquet_pattern = possible_patterns[0]
                print(f"📂 Parquet pattern: {parquet_pattern}")
            else:
                return False, "No equipment specified"
            
            # Build WHERE clause
            where_conditions = [
                f"t_sampling_time >= TIMESTAMP '{time_start}'",
                f"t_sampling_time <= TIMESTAMP '{time_end}'"
            ]
            
            # ENHANCED: Process filter_selections correctly
            # Extract filter key after the number prefix (e.g., "1_n_bank" -> "n_bank")
            for equipment_key, filters in filter_selections.items():
                if isinstance(filters, dict):
                    # If filters is a dictionary, iterate through key-value pairs
                    for filter_key, filter_value in filters.items():
                        if filter_value and str(filter_value).strip():
                            # Extract the actual filter name after the number prefix
                            if '_' in filter_key and filter_key.split('_')[0].isdigit():
                                actual_filter_key = '_'.join(filter_key.split('_')[1:])  # Remove number prefix
                            else:
                                actual_filter_key = filter_key
                            where_conditions.append(f"{actual_filter_key} = '{filter_value}'")
                            print(f"🏷️ Parquet filter: {actual_filter_key} = {filter_value}")
                else:
                    # If filters is a single value, use equipment_key as the filter
                    if filters and str(filters).strip():
                        # Extract the actual filter name after the number prefix
                        if '_' in equipment_key and equipment_key.split('_')[0].isdigit():
                            actual_filter_key = '_'.join(equipment_key.split('_')[1:])  # Remove number prefix
                        else:
                            actual_filter_key = equipment_key
                        where_conditions.append(f"{actual_filter_key} = '{filters}'")
                        print(f"🏷️ Parquet filter: {actual_filter_key} = {filters}")
            
            # Build GROUP BY clause
            group_by_clause = f"time_bucket(INTERVAL '{window_seconds} seconds', CAST(t_sampling_time AS TIMESTAMP), TIMESTAMP '{time_start}')"
            
            # Combine query parts
            query = f"""
            SELECT {', '.join(select_columns)}
            FROM read_parquet('{parquet_pattern}')
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
    
    # =================== UTILITY METHODS ===================
    
    @staticmethod
    def generate_sample_time_ranges() -> List[Dict]:
        """Generate sample time ranges for UI dropdown"""
        now = datetime.now()
        
        return [
            {
                "label": "Last 15 minutes",
                "value": "last_15m",
                "start": (now - timedelta(minutes=15)).isoformat(),
                "end": now.isoformat()
            },
            {
                "label": "Last 1 hour",
                "value": "last_1h",
                "start": (now - timedelta(hours=1)).isoformat(),
                "end": now.isoformat()
            },
            {
                "label": "Last 6 hours",
                "value": "last_6h",
                "start": (now - timedelta(hours=6)).isoformat(),
                "end": now.isoformat()
            },
            {
                "label": "Last 24 hours",
                "value": "last_24h",
                "start": (now - timedelta(days=1)).isoformat(),
                "end": now.isoformat()
            },
            {
                "label": "Last 7 days",
                "value": "last_7d",
                "start": (now - timedelta(days=7)).isoformat(),
                "end": now.isoformat()
            }
        ]
    
    @staticmethod
    def calculate_time_range(range_type: str, custom_start: str = None, custom_end: str = None) -> Dict:
        """Calculate time range based on type - ENHANCED"""
        now = datetime.now()
        
        if range_type == "custom" and custom_start and custom_end:
            return {
                "start": custom_start,
                "end": custom_end,
                "range_type": "custom"
            }
        elif range_type == "last_15m":
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
        """Validate widget metadata before query generation - ENHANCED"""
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
        
        # Check filter selections format
        filter_selections = widget_config.get('filter_selections', {})
        if not isinstance(filter_selections, dict):
            errors.append("Filter selections must be a dictionary")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def get_supported_aggregation_functions() -> List[Dict[str, str]]:
        """Get list of supported aggregation functions for different data sources"""
        return [
            {"name": "mean", "label": "Average", "description": "Calculate average values"},
            {"name": "max", "label": "Maximum", "description": "Calculate maximum values"},
            {"name": "min", "label": "Minimum", "description": "Calculate minimum values"},
            {"name": "sum", "label": "Sum", "description": "Calculate sum of values"},
            {"name": "count", "label": "Count", "description": "Count non-null values"}
        ]
    
    @staticmethod
    def estimate_query_complexity(equipment_count: int, signal_count: int, 
                                 filter_count: int, time_range_hours: float) -> Dict[str, Any]:
        """Estimate query complexity and performance characteristics"""
        # Simple complexity calculation
        base_complexity = equipment_count * signal_count
        filter_complexity = filter_count * 0.5
        time_complexity = min(time_range_hours / 24, 10)  # Cap at 10 for very long ranges
        
        total_complexity = base_complexity + filter_complexity + time_complexity
        
        if total_complexity < 5:
            complexity_level = "Low"
            estimated_time = "< 1s"
        elif total_complexity < 15:
            complexity_level = "Medium"
            estimated_time = "1-3s"
        else:
            complexity_level = "High"
            estimated_time = "3-10s"
        
        return {
            "complexity_level": complexity_level,
            "estimated_time": estimated_time,
            "total_complexity_score": round(total_complexity, 2),
            "factors": {
                "equipment_count": equipment_count,
                "signal_count": signal_count,
                "filter_count": filter_count,
                "time_range_hours": time_range_hours
            },
            "recommendations": QueryGenerationService._get_complexity_recommendations(complexity_level)
        }
    
    @staticmethod
    def _get_complexity_recommendations(complexity_level: str) -> List[str]:
        """Get recommendations based on query complexity"""
        if complexity_level == "Low":
            return [
                "Query should execute quickly",
                "Consider increasing time range for more data points"
            ]
        elif complexity_level == "Medium":
            return [
                "Consider using larger window periods to reduce data points",
                "Monitor query performance"
            ]
        else:  # High
            return [
                "Use larger window periods (1h or more) to improve performance",
                "Consider reducing time range or number of signals",
                "Split into multiple smaller queries if needed"
            ]
    
    @staticmethod
    def generate_query_preview(db: Session, widget_config: Dict, time_range: Dict,
                              window_period: str = "auto", connection_id: str = None) -> Dict[str, Any]:
        """
        Generate a query preview without executing it
        Useful for debugging and query optimization
        """
        try:
            # Generate the query
            success, query, data_source_type, connection_config, window_info = QueryGenerationService.generate_widget_query(
                db, widget_config, time_range, window_period, connection_id
            )
            
            if not success:
                return {
                    "success": False,
                    "error": query,
                    "data_source_type": data_source_type
                }
            
            # Estimate complexity
            equipment_count = len(widget_config.get('equipment_ids', []))
            signal_count = len(widget_config.get('signal_ids', []))
            filter_count = len(widget_config.get('filter_selections', {}))
            
            try:
                start_dt = datetime.fromisoformat(time_range['start'].replace('Z', '+00:00').replace('+00:00', ''))
                end_dt = datetime.fromisoformat(time_range['end'].replace('Z', '+00:00').replace('+00:00', ''))
                time_range_hours = (end_dt - start_dt).total_seconds() / 3600
            except:
                time_range_hours = 1.0
            
            complexity_info = QueryGenerationService.estimate_query_complexity(
                equipment_count, signal_count, filter_count, time_range_hours
            )
            
            return {
                "success": True,
                "query": query,
                "data_source_type": data_source_type,
                "connection_config": {
                    "type": data_source_type,
                    "name": connection_config.get('name', 'Unknown')
                },
                "window_info": window_info,
                "complexity": complexity_info,
                "query_stats": {
                    "length": len(query),
                    "line_count": len(query.split('\n')),
                    "estimated_result_columns": signal_count + 1,  # +1 for timestamp
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Query preview generation failed: {str(e)}"
            }
    
    @staticmethod
    def validate_connection_for_query(db: Session, connection_id: str, 
                                    widget_config: Dict) -> Tuple[bool, List[str]]:
        """
        Validate that a connection is suitable for a specific widget configuration
        """
        errors = []
        warnings = []
        
        try:
            # Get connection
            connection = datasource_crud.get_data_connection_by_id(db, connection_id)
            if not connection:
                errors.append(f"Connection {connection_id} not found")
                return False, errors
            
            if connection.status != 'active':
                errors.append(f"Connection {connection.name} is not active")
            
            connection_config = datasource_crud.get_connection_config_dict(db, connection_id)
            data_source_type = connection.db_type.lower()
            
            # Validate based on data source type
            if data_source_type == 'influxdb':
                # InfluxDB specific validations
                required_fields = ['url', 'token', 'org', 'bucket']
                for field in required_fields:
                    if not connection_config.get(field):
                        errors.append(f"InfluxDB connection missing required field: {field}")
                
                # Check if InfluxDB client is available
                try:
                    from influxdb_client import InfluxDBClient
                except ImportError:
                    errors.append("InfluxDB client library not installed. Run: pip install influxdb-client")
                
            elif data_source_type in ['sqlite3', 'sqlite']:
                # SQLite specific validations
                db_path = connection_config.get('database_path') or connection_config.get('db_path')
                if not db_path:
                    errors.append("SQLite connection missing database path")
                else:
                    import os
                    if not os.path.exists(db_path):
                        errors.append(f"SQLite database file not found: {db_path}")
                
            elif data_source_type == 'parquet':
                # Parquet specific validations
                base_path = connection_config.get('base_path') or connection_config.get('file_path')
                if not base_path:
                    errors.append("Parquet connection missing base path or file path")
                else:
                    import os
                    if not os.path.exists(base_path):
                        errors.append(f"Parquet base path not found: {base_path}")
            
            # Validate widget compatibility
            equipment_ids = widget_config.get('equipment_ids', [])
            signal_ids = widget_config.get('signal_ids', [])
            
            if not equipment_ids:
                warnings.append("No equipment selected in widget configuration")
            
            if not signal_ids:
                warnings.append("No signals selected in widget configuration")
            
            return len(errors) == 0, errors + [f"Warning: {w}" for w in warnings]
            
        except Exception as e:
            errors.append(f"Connection validation error: {str(e)}")
            return False, errors
    
    @staticmethod
    def get_query_optimization_suggestions(data_source_type: str, window_info: Dict, 
                                         signal_count: int) -> List[Dict[str, str]]:
        """
        Get optimization suggestions based on query characteristics
        """
        suggestions = []
        
        estimated_points = window_info.get('estimated_points', 0)
        window_seconds = window_info.get('window_seconds', 3600)
        
        # General optimization suggestions
        if estimated_points > 200:
            suggestions.append({
                "type": "performance",
                "title": "High Data Volume",
                "description": f"Query will return ~{estimated_points} points. Consider increasing window period to {window_seconds * 2}s for better performance."
            })
        
        if signal_count > 10:
            suggestions.append({
                "type": "performance", 
                "title": "Many Signals",
                "description": f"Querying {signal_count} signals. Consider splitting into multiple widgets for better visualization."
            })
        
        # Data source specific suggestions
        if data_source_type.lower() == 'influxdb':
            suggestions.append({
                "type": "optimization",
                "title": "InfluxDB Optimization",
                "description": "InfluxDB queries benefit from specific field filters. Ensure signals match InfluxDB field names."
            })
            
            if window_seconds < 60:
                suggestions.append({
                    "type": "warning",
                    "title": "Small Window Period",
                    "description": "Very small window periods may not be efficient with InfluxDB. Consider 1m or larger windows."
                })
        
        elif data_source_type.lower() == 'parquet':
            suggestions.append({
                "type": "optimization",
                "title": "Parquet Optimization", 
                "description": "Parquet queries are optimized for time-based partitioning. Ensure data is partitioned by time."
            })
            
        elif data_source_type.lower() in ['sqlite3', 'sqlite']:
            if estimated_points > 1000:
                suggestions.append({
                    "type": "performance",
                    "title": "SQLite Large Query",
                    "description": "Large SQLite queries may be slow. Consider adding indexes on timestamp and filter columns."
                })
        
        return suggestions
    
    @staticmethod
    def test_query_syntax(db: Session, widget_config: Dict, time_range: Dict,
                         window_period: str = "auto", connection_id: str = None) -> Dict[str, Any]:
        """
        Test query syntax without executing the full query
        Useful for development and debugging
        """
        try:
            # Generate query
            success, query, data_source_type, connection_config, window_info = QueryGenerationService.generate_widget_query(
                db, widget_config, time_range, window_period, connection_id
            )
            
            if not success:
                return {
                    "success": False,
                    "error": query,
                    "syntax_valid": False
                }
            
            # Basic syntax validation
            syntax_errors = []
            
            if data_source_type.lower() == 'influxdb':
                # Basic Flux syntax checks
                if not query.strip().startswith('from('):
                    syntax_errors.append("InfluxDB Flux query should start with 'from('")
                
                if '|> yield' not in query:
                    syntax_errors.append("InfluxDB Flux query should end with '|> yield'")
                
                # Check for common Flux syntax issues
                if query.count('(') != query.count(')'):
                    syntax_errors.append("Unmatched parentheses in Flux query")
                    
            elif data_source_type.lower() in ['sqlite3', 'sqlite', 'parquet']:
                # Basic SQL syntax checks
                if not query.strip().upper().startswith('SELECT'):
                    syntax_errors.append("SQL query should start with SELECT")
                
                if 'FROM' not in query.upper():
                    syntax_errors.append("SQL query missing FROM clause")
                
                if 'ORDER BY' not in query.upper():
                    syntax_errors.append("SQL query should include ORDER BY for time series data")
            
            return {
                "success": True,
                "syntax_valid": len(syntax_errors) == 0,
                "syntax_errors": syntax_errors,
                "query": query,
                "data_source_type": data_source_type,
                "query_length": len(query),
                "estimated_execution_time": QueryGenerationService._estimate_execution_time(
                    data_source_type, window_info, len(widget_config.get('signal_ids', []))
                )
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Query syntax test failed: {str(e)}",
                "syntax_valid": False
            }
    
    @staticmethod
    def _estimate_execution_time(data_source_type: str, window_info: Dict, signal_count: int) -> str:
        """Estimate query execution time based on characteristics"""
        estimated_points = window_info.get('estimated_points', 100)
        
        # Base time estimates (in seconds)
        base_times = {
            'sqlite3': 0.1,
            'sqlite': 0.1,
            'parquet': 0.5,
            'influxdb': 1.0
        }
        
        base_time = base_times.get(data_source_type.lower(), 1.0)
        
        # Adjust for data volume and complexity
        complexity_factor = (estimated_points / 100) * (signal_count / 5)
        estimated_seconds = base_time * (1 + complexity_factor)
        
        if estimated_seconds < 1:
            return "< 1s"
        elif estimated_seconds < 5:
            return f"~{round(estimated_seconds)}s"
        else:
            return f"{round(estimated_seconds)}s+"