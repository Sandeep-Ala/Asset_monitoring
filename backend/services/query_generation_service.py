# services/query_generation_service.py - Auto Query Generation from Widget Metadata

from typing import Dict, List, Tuple, Optional, Any
from sqlalchemy.orm import Session
import services.meta_crud as meta_crud
import services.datasource_crud as datasource_crud
from datetime import datetime, timedelta
import json

class QueryGenerationService:
    """
    Service to generate database queries from widget metadata
    Supports both SQLite and Parquet data sources
    """
    
    @staticmethod
    def generate_widget_query(db: Session, widget_config: Dict, time_range: Dict, 
                            window_period: str = "auto", connection_id: str = None) -> Tuple[bool, str, str, Dict, Dict]:
        """
        Generate query for widget data retrieval with window period support
        
        Returns: (success, query, data_source_type, connection_config, window_info)
        """
        try:
            # Import here to avoid circular imports
            from config import calculate_optimal_window_period, MAX_POINTS_PER_WIDGET
            
            # Extract widget metadata
            equipment_ids = widget_config.get('equipment_ids', [])
            signal_ids = widget_config.get('signal_ids', [])
            filter_selections = widget_config.get('filter_selections', {})
            
            if not equipment_ids or not signal_ids:
                return False, "Equipment and signals are required", "", {}, {}
            
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
            else:
                from config import WINDOW_PERIOD_OPTIONS
                window_seconds = WINDOW_PERIOD_OPTIONS.get(window_period, 3600)
                
                # Calculate estimated points
                time_start = time_range.get('start', '')
                time_end = time_range.get('end', '')
                try:
                    from datetime import datetime
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
            
            # Get equipment and signal information
            equipment_info = []
            signal_info = []
            
            for equipment_id in equipment_ids:
                equipment = meta_crud.get_equipment_by_id(db, equipment_id)
                model_info = meta_crud.get_master_model_by_id(db,equipment.model_id)
                if equipment:
                    equipment_info.append({
                        'id': equipment_id,
                        'name': equipment.name,
                        'location': equipment.location,
                        'model_name':model_info.name    # bms or rbms floder partation equipment=rbms
                    })
            
            for signal_id in signal_ids:
                signal = meta_crud.get_equipment_signal_by_id(db, signal_id)
                if signal:
                    signal_info.append({
                        'id': signal_id,
                        'key': signal.key,
                        'value': signal.value,
                        'unit': signal.unit,
                        'equipment_id': signal.eqp_id
                    })
            
            # Determine data source (for now, use first active connection)
            if not connection_id:
                connections = datasource_crud.get_all_data_connections(db)
                active_connections = [conn for conn in connections if conn.status == 'active']
                if not active_connections:
                    return False, "No active data connections found", "", {}, {}
                connection = active_connections[0]
                connection_id = connection.id
            else:
                connection = datasource_crud.get_data_connection_by_id(db, connection_id)
                if not connection:
                    return False, f"Connection {connection_id} not found", "", {}, {}
            
            # Get connection configuration
            connection_config = datasource_crud.get_connection_config_dict(db, connection_id)
            data_source_type = connection.db_type
            
            # Generate query based on data source type
            if data_source_type.lower() == 'sqlite3':
                success, query = QueryGenerationService._generate_sqlite_query_with_window(
                    equipment_info, signal_info, filter_selections, time_range, connection_config, window_info
                )
            elif data_source_type.lower() == 'parquet':
                
                success, query = QueryGenerationService._generate_parquet_query_with_window(
                    equipment_info, signal_info, filter_selections, time_range, connection_config, window_info
                )
            else:
                return False, f"Unsupported data source type: {data_source_type}", "", {}, {}
            
            if success:
                return True, query, data_source_type, connection_config, window_info
            else:
                return False, query, data_source_type, connection_config, window_info
                
        except Exception as e:
            return False, f"Query generation error: {str(e)}", "", {}, {}
    
    @staticmethod
    def _generate_sqlite_query_with_window(equipment_info: List[Dict], signal_info: List[Dict], 
                                          filter_selections: Dict, time_range: Dict, 
                                          connection_config: Dict, window_info: Dict) -> Tuple[bool, str]:
        """Generate SQLite query with time_bucket aggregation"""
        try:
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
                select_columns.append(f"AVG({signal_key}) AS \"{signal_alias}\"")
            
            select_clause = "SELECT " + ", ".join(select_columns)
            
            # Determine table name (assume equipment name maps to table)
            if equipment_info:
                table_name = f"t_{equipment_info[0]['name'].lower()}"
            else:
                return False, "No equipment specified"
            
            # Build WHERE clause
            where_conditions = [
                f"t_sampling_time >= '{time_start}'",
                f"t_sampling_time <= '{time_end}'"
            ]
            
            # Add filter selections
            for equipment_key, filters in filter_selections.items():
                for filter_key, filter_value in filters.items():
                    where_conditions.append(f"{filter_key} = '{filter_value}'")
            
            where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Build complete query with GROUP BY for time_bucket
            query = f"""
            {select_clause}
            FROM {table_name}
            {where_clause}
            GROUP BY 1
            ORDER BY timestamp ASC
            """
            
            return True, query.strip()
            
        except Exception as e:
            return False, f"SQLite query generation error: {str(e)}"
    
   
    @staticmethod
    def _generate_parquet_query_with_window(equipment_info: List[Dict], signal_info: List[Dict], 
                                            filter_selections: Dict, time_range: Dict, 
                                            connection_config: Dict, window_info: Dict) -> Tuple[bool, str]:
        """Generate Parquet/DuckDB query with time_bucket aggregation"""
        try:
            # Extract time range and window
            time_start = time_range.get('start', '')
            time_end = time_range.get('end', '')
            window_seconds = window_info.get('window_seconds', 3600)
            
            if not time_start or not time_end:
                return False, "Time range start and end are required"
            
            # Get base path from connection config
            base_path = connection_config.get('base_path', '')
            if not base_path:
                return False, "Base path not found in connection config"
            
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
                select_columns.append(f"AVG({signal_key}) AS \"{signal_alias}\"")
            
            select_clause = "SELECT " + ", ".join(select_columns)
            
            # Build parquet file path pattern
            # FIXED: Handle Windows paths with proper escaping and normalization
            if equipment_info:
                equipment_name = equipment_info[0]['model_name'].lower()
                # Normalize path separators for cross-platform compatibility
                normalized_base_path = base_path.replace('\\', '/')
                parquet_pattern = f"{normalized_base_path}/**/equipment={equipment_name}/dcu=*/*.parquet"
            else:
                return False, "No equipment specified"
            
            # Build WHERE clause
            where_conditions = [
                f"t_sampling_time >= '{time_start}'",
                f"t_sampling_time <= '{time_end}'"
            ]
            
            # FIXED: Process filter_selections correctly
            # Extract filter key after the number prefix (e.g., "1_n_bank" -> "n_bank")
            for equipment_key, filters in filter_selections.items():
                if isinstance(filters, dict):
                    # If filters is a dictionary, iterate through key-value pairs
                    for filter_key, filter_value in filters.items():
                        # Extract the actual filter name after the number prefix
                        if '_' in filter_key:
                            actual_filter_key = '_'.join(filter_key.split('_')[1:])  # Remove number prefix
                        else:
                            actual_filter_key = filter_key
                        where_conditions.append(f"{actual_filter_key} = '{filter_value}'")
                else:
                    # If filters is a single value, use equipment_key as the filter
                    # Extract the actual filter name after the number prefix
                    if '_' in equipment_key:
                        actual_filter_key = '_'.join(equipment_key.split('_')[1:])  # Remove number prefix
                    else:
                        actual_filter_key = equipment_key
                    where_conditions.append(f"{actual_filter_key} = '{filters}'")
            
            where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Build DuckDB query for parquet files with GROUP BY for time_bucket
            query = f"""
            {select_clause}
            FROM read_parquet('{parquet_pattern}')
            {where_clause}
            GROUP BY 1
            ORDER BY timestamp ASC
            """
            
            return True, query.strip()
            
        except Exception as e:
            return False, f"Parquet query generation error: {str(e)}"
    
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
        """Calculate time range based on type"""
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
        """Validate widget metadata before query generation"""
        errors = []
        
        # Check equipment IDs
        equipment_ids = widget_config.get('equipment_ids', [])
        if not equipment_ids:
            errors.append("At least one equipment must be selected")
        else:
            for equipment_id in equipment_ids:
                equipment = meta_crud.get_equipment_by_id(db, equipment_id)
                if not equipment:
                    errors.append(f"Equipment ID {equipment_id} not found")
        
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