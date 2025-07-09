# services/data_retrieval_service.py - Execute Queries and Retrieve Data for Widgets

import sqlite3
import duckdb
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from sqlalchemy.orm import Session
import os
from datetime import datetime
import json

class DataRetrievalService:
    """
    Service to execute generated queries on different data sources
    and return formatted data for widget visualization
    """
    
    @staticmethod
    def execute_widget_query(query: str, data_source_type: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """
        Execute widget query on specified data source
        
        Returns: (success, data_rows, error_message)
        """
        try:
            if data_source_type.lower() == 'sqlite3':
                return DataRetrievalService._execute_sqlite_query(query, connection_config)
            elif data_source_type.lower() == 'parquet':
                return DataRetrievalService._execute_parquet_query(query, connection_config)
            else:
                return False, [], f"Unsupported data source type: {data_source_type}"
                
        except Exception as e:
            return False, [], f"Query execution error: {str(e)}"
    
    @staticmethod
    def _execute_sqlite_query(query: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute query on SQLite database"""
        try:
            db_path = connection_config.get('database_path')
            if not db_path or not os.path.exists(db_path):
                return False, [], "Database file not found"
            
            # Connect to SQLite
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA journal_mode = WAL")  # Performance optimization
            conn.execute("PRAGMA synchronous = NORMAL")
            
            # Execute query
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            data_rows = []
            for row in rows:
                row_dict = {}
                for i, column in enumerate(columns):
                    value = row[i]
                    # Handle different data types
                    if isinstance(value, (int, float)):
                        row_dict[column] = round(value, 4) if isinstance(value, float) else value
                    else:
                        row_dict[column] = str(value) if value is not None else None
                data_rows.append(row_dict)
            
            conn.close()
            
            return True, data_rows, ""
            
        except sqlite3.Error as e:
            return False, [], f"SQLite error: {str(e)}"
        except Exception as e:
            return False, [], f"SQLite execution error: {str(e)}"
    
    @staticmethod
    def _execute_parquet_query(query: str, connection_config: Dict) -> Tuple[bool, List[Dict], str]:
        """Execute query on Parquet files using DuckDB"""
        try:
            base_path = connection_config.get('base_path')
            if not base_path or not os.path.exists(base_path):
                return False, [], "Base path not found"
            
            # Connect to DuckDB (in-memory)
            conn = duckdb.connect(database=':memory:')
            
            # Execute query
            result = conn.execute(query).fetchdf()
            
            # Convert DataFrame to list of dictionaries
            if result.empty:
                return True, [], "No data found for the specified time range and filters"
            
            # Round numeric columns
            for col in result.columns:
                if result[col].dtype in ['float64', 'float32']:
                    result[col] = result[col].round(4)
                elif result[col].dtype in ['int64', 'int32']:
                    result[col] = result[col].astype(int)
            
            # Convert to dictionary format
            data_rows = result.to_dict(orient='records')
            
            # Ensure timestamp is string format for JSON serialization
            for row in data_rows:
                for key, value in row.items():
                    if key == 'timestamp' and value is not None:
                        if isinstance(value, pd.Timestamp):
                            row[key] = value.isoformat()
                        else:
                            row[key] = str(value)
                    elif pd.isna(value):
                        row[key] = None
            
            conn.close()
            
            return True, data_rows, ""
            
        except Exception as e:
            return False, [], f"Parquet execution error: {str(e)}"
    
    @staticmethod
    def format_data_for_chart(data_rows: List[Dict], widget_config: Dict) -> Dict[str, Any]:
        """
        Format data for Chart.js consumption
        
        Returns formatted data structure for line charts
        """
        try:
            if not data_rows:
                return {
                    "labels": [],
                    "datasets": [],
                    "isEmpty": True,
                    "message": "No data available"
                }
            
            # Extract timestamps for x-axis labels
            timestamps = []
            for row in data_rows:
                timestamp = row.get('timestamp')
                if timestamp:
                    # Format timestamp for display
                    try:
                        dt = pd.to_datetime(timestamp)
                        formatted_time = dt.strftime('%H:%M:%S')
                        timestamps.append(formatted_time)
                    except:
                        timestamps.append(str(timestamp))
                else:
                    timestamps.append('')
            
            # Get signal information from widget config
            equipment_ids = widget_config.get('equipment_ids', [])
            signal_ids = widget_config.get('signal_ids', [])
            styling_config = widget_config.get('styling_config', {})
            
            # Extract data columns (exclude timestamp)
            data_columns = []
            for key in data_rows[0].keys():
                if key != 'timestamp':
                    data_columns.append(key)
            
            # Create datasets for Chart.js
            datasets = []
            colors = styling_config.get('colors', ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0'])
            line_styles = styling_config.get('lineStyles', ['solid'])
            
            for i, column in enumerate(data_columns):
                # Extract values for this signal
                values = []
                for row in data_rows:
                    value = row.get(column)
                    if value is not None and value != '':
                        try:
                            values.append(float(value))
                        except (ValueError, TypeError):
                            values.append(None)
                    else:
                        values.append(None)
                
                # Determine color and line style
                color = colors[i % len(colors)] if colors else '#36a2eb'
                line_style = line_styles[i % len(line_styles)] if line_styles else 'solid'
                
                # Create dataset
                dataset = {
                    "label": column,
                    "data": values,
                    "borderColor": color,
                    "backgroundColor": color + '20',  # Add transparency
                    "borderWidth": 2,
                    "fill": False,
                    "tension": 0.1,  # Smooth curves
                    "pointRadius": 3,
                    "pointHoverRadius": 5
                }
                
                # Apply line style
                if line_style == 'dashed':
                    dataset["borderDash"] = [5, 5]
                elif line_style == 'dotted':
                    dataset["borderDash"] = [2, 2]
                
                datasets.append(dataset)
            
            return {
                "labels": timestamps,
                "datasets": datasets,
                "isEmpty": False,
                "totalPoints": len(timestamps),
                "timeRange": {
                    "start": timestamps[0] if timestamps else "",
                    "end": timestamps[-1] if timestamps else ""
                }
            }
            
        except Exception as e:
            return {
                "labels": [],
                "datasets": [],
                "isEmpty": True,
                "message": f"Data formatting error: {str(e)}"
            }
    
    @staticmethod
    def get_widget_data_with_window(db: Session, widget_id: str, time_range: Dict, window_period: str = "auto", connection_id: str = None) -> Tuple[bool, Dict, str]:
        """
        Complete widget data retrieval pipeline with window period support
        
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
            print(f'widget_config:{widget_config}')
            
            # Validate widget metadata
            is_valid, errors = QueryGenerationService.validate_widget_metadata(db, widget_config)
            print(f'is_valid:{is_valid}')
            print(f'errors:{errors}')
            
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
            
            # Format data for chart
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
            formatted_data["actual_points"] = len(data_rows)
            
            return True, formatted_data, ""
            
        except Exception as e:
            return False, {}, f"Widget data retrieval error: {str(e)}"
    
    @staticmethod
    def get_bulk_widget_data_with_window(db: Session, page_id: str, time_range: Dict, window_period: str = "auto", connection_id: str = None) -> Dict[str, Any]:
        """
        Get data for all widgets on a page in bulk with window period support
        
        Returns: {widget_id: formatted_data, ...}
        """
        try:
            from services.widget_crud import get_widgets_by_page
            
            widgets = get_widgets_by_page(db, page_id)
            bulk_data = {}
            
            for widget in widgets:
                success, data, error = DataRetrievalService.get_widget_data_with_window(
                    db, widget.widget_id, time_range, window_period, connection_id
                )
                
                if success:
                    bulk_data[widget.widget_id] = data
                else:
                    bulk_data[widget.widget_id] = {
                        "labels": [],
                        "datasets": [],
                        "isEmpty": True,
                        "message": error,
                        "window_info": {
                            "window_period": window_period,
                            "error": True
                        }
                    }
            
            return bulk_data
            
        except Exception as e:
            return {"error": f"Bulk data retrieval error: {str(e)}"}
    
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
            time_diff = end_dt - start_dt
            if time_diff.days > 30:
                return False, "Time range cannot exceed 30 days"
            
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