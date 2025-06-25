# services/schema_discovery_service.py

import sqlite3
import os
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
import services.datasource_crud as crud

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
            return True, tables, "Tables retrieved successfully"
            
        except sqlite3.Error as e:
            return False, [], f"SQLite error: {str(e)}"
        except Exception as e:
            return False, [], f"Unexpected error: {str(e)}"
    
    @staticmethod
    def get_sqlite_columns(config: Dict[str, str], table_name: str, quick_mode: bool = False) -> Tuple[bool, List[Dict], str]:
        """Get all columns for a specific SQLite table with performance optimizations"""
        try:
            db_path = config.get('database_path')
            if not db_path or not os.path.exists(db_path):
                return False, [], "Database file not found"
            
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA journal_mode = WAL")  # Performance optimization
            conn.execute("PRAGMA synchronous = NORMAL")  # Performance optimization
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table_name,))
            
            if not cursor.fetchone():
                conn.close()
                return False, [], f"Table '{table_name}' not found"
            
            # Get column information
            cursor.execute(f"PRAGMA table_info(`{table_name}`)")
            pragma_info = cursor.fetchall()
            
            # Get total row count once (with limit for performance)
            cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` LIMIT 50000")
            total_rows_result = cursor.fetchone()
            total_rows = total_rows_result[0] if total_rows_result else 0
            
            if total_rows >= 50000:
                total_rows = "50k+"
                is_large_table = True
            else:
                is_large_table = False
            
            columns = []
            for col_info in pragma_info:
                cid, name, data_type, not_null, default_value, pk = col_info
                
                # Initialize column data
                column_data = {
                    "name": name,
                    "data_type": data_type,
                    "nullable": not bool(not_null),
                    "primary_key": bool(pk),
                    "default_value": default_value,
                    "total_rows": total_rows
                }
                
                if quick_mode or is_large_table:
                    # Quick mode: minimal analysis for large tables
                    column_data.update({
                        "distinct_count": "Not analyzed",
                        "distinctness_ratio": 0,
                        "sample_values": [],
                        "category": SchemaDiscoveryService._classify_column_type_simple(name, data_type),
                        "suggested_for": []
                    })
                else:
                    # Full analysis for smaller tables
                    try:
                        # Get sample values (limit to 3 for performance)
                        cursor.execute(f"SELECT `{name}` FROM `{table_name}` WHERE `{name}` IS NOT NULL LIMIT 3")
                        sample_values = [str(row[0]) for row in cursor.fetchall()]
                        
                        # Get distinct count (with reasonable limit)
                        cursor.execute(f"SELECT COUNT(DISTINCT `{name}`) as distinct_count FROM `{table_name}` LIMIT 10000")
                        distinct_count_result = cursor.fetchone()
                        distinct_count = distinct_count_result[0] if distinct_count_result else 0
                        
                        if isinstance(total_rows, int) and total_rows > 0:
                            distinctness_ratio = distinct_count / total_rows
                        else:
                            distinctness_ratio = 0
                        
                        # Classify column types
                        column_category = SchemaDiscoveryService._classify_column_type(
                            name, data_type, distinctness_ratio, sample_values
                        )
                        
                        column_data.update({
                            "distinct_count": distinct_count,
                            "distinctness_ratio": round(distinctness_ratio, 3),
                            "sample_values": sample_values,
                            "category": column_category,
                            "suggested_for": SchemaDiscoveryService._get_suggested_usage(column_category, distinctness_ratio)
                        })
                        
                    except sqlite3.Error as e:
                        # If analysis fails, fall back to simple classification
                        column_data.update({
                            "distinct_count": "Error",
                            "distinctness_ratio": 0,
                            "sample_values": [],
                            "category": SchemaDiscoveryService._classify_column_type_simple(name, data_type),
                            "suggested_for": []
                        })
                
                columns.append(column_data)
            
            conn.close()
            message = "Columns retrieved successfully"
            if quick_mode or is_large_table:
                message += " (quick mode - limited analysis for performance)"
            
            return True, columns, message
            
        except sqlite3.Error as e:
            return False, [], f"SQLite error: {str(e)}"
        except Exception as e:
            return False, [], f"Unexpected error: {str(e)}"
    
    @staticmethod
    def _classify_column_type(name: str, data_type: str, distinctness_ratio: float, sample_values: List[str]) -> str:
        """Classify column into categories for UI suggestions"""
        name_lower = name.lower()
        data_type_lower = data_type.lower()
        
        # Time-related columns
        if any(keyword in name_lower for keyword in ['time', 'date', 'timestamp', 'created', 'updated']):
            return "timestamp"
        
        # ID columns
        if any(keyword in name_lower for keyword in ['id', '_id', 'uuid', 'key']) or distinctness_ratio > 0.9:
            return "identifier"
        
        # Boolean-like columns
        if data_type_lower in ['boolean', 'bool'] or all(val in ['0', '1', 'true', 'false', 'True', 'False'] for val in sample_values if val):
            return "boolean"
        
        # Numeric columns
        if data_type_lower in ['integer', 'int', 'real', 'numeric', 'decimal', 'float', 'double']:
            if distinctness_ratio < 0.1:  # Low distinctness suggests categorical
                return "categorical_numeric"
            else:
                return "numeric"
        
        # Text columns
        if data_type_lower in ['text', 'varchar', 'char', 'string']:
            if distinctness_ratio < 0.1:  # Low distinctness suggests categorical
                return "categorical_text"
            else:
                return "text"
        
    @staticmethod
    def _get_suggested_usage(category: str, distinctness_ratio: float) -> List[str]:
        """Get suggested usage for UI (signals, filters, specs, etc.)"""
        suggestions = []
        
        if category == "timestamp":
            suggestions = ["timestamp_field"]
        elif category == "identifier":
            suggestions = ["equipment_identifier"]
        elif category == "boolean":
            suggestions = ["signals", "specs"]
        elif category == "numeric":
            suggestions = ["signals", "specs"]
        elif category == "categorical_numeric" or category == "categorical_text":
            suggestions = ["filters", "equipment_identifier"]
            if distinctness_ratio < 0.05:  # Very low distinctness
                suggestions.append("specs")
        elif category == "text":
            suggestions = ["specs", "documentation"]
        
        return suggestions
    
    @staticmethod
    def _classify_column_type_simple(name: str, data_type: str) -> str:
        """Simplified column classification for large tables (no data analysis)"""
        name_lower = name.lower()
        data_type_lower = data_type.lower()
        
        # Time-related columns
        if any(keyword in name_lower for keyword in ['time', 'date', 'timestamp', 'created', 'updated']):
            return "timestamp"
        
        # ID columns
        if any(keyword in name_lower for keyword in ['id', '_id', 'uuid', 'key']):
            return "identifier"
        
        # Boolean-like columns
        if data_type_lower in ['boolean', 'bool'] or any(keyword in name_lower for keyword in ['is_', 'has_', 'can_', 'flag']):
            return "boolean"
        
        # Numeric columns
        if data_type_lower in ['integer', 'int', 'real', 'numeric', 'decimal', 'float', 'double']:
            return "numeric"
        
        # Text columns
        if data_type_lower in ['text', 'varchar', 'char', 'string']:
            return "text"
        
        return "unknown"
        """Get suggested usage for UI (signals, filters, specs, etc.)"""
        suggestions = []
        
        if category == "timestamp":
            suggestions = ["timestamp_field"]
        elif category == "identifier":
            suggestions = ["equipment_identifier"]
        elif category == "boolean":
            suggestions = ["signals", "specs"]
        elif category == "numeric":
            suggestions = ["signals", "specs"]
        elif category == "categorical_numeric" or category == "categorical_text":
            suggestions = ["filters", "equipment_identifier"]
            if distinctness_ratio < 0.05:  # Very low distinctness
                suggestions.append("specs")
        elif category == "text":
            suggestions = ["specs", "documentation"]
        
        return suggestions
    
    @staticmethod
    def get_complete_schema(config: Dict[str, str], quick_mode: bool = True) -> Tuple[bool, Dict, str]:
        """Get complete database schema information with performance optimization"""
        try:
            # Get tables
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
                
                # Use quick mode for large tables or when requested
                use_quick_mode = quick_mode or (isinstance(table['row_count'], str) and 'k+' in str(table['row_count']))
                
                success, columns, _ = SchemaDiscoveryService.get_sqlite_columns(
                    config, table["name"], quick_mode=use_quick_mode
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
            
            return True, schema, "Schema retrieved successfully (optimized for performance)"
            
        except Exception as e:
            return False, {}, f"Error retrieving schema: {str(e)}"
    
    # Placeholder methods for future database types
    @staticmethod
    def get_influxdb_measurements(config: Dict[str, str]) -> Tuple[bool, List[Dict], str]:
        """Get InfluxDB measurements (placeholder)"""
        return False, [], "InfluxDB schema discovery not yet implemented"
    
    @staticmethod
    def get_parquet_files(config: Dict[str, str]) -> Tuple[bool, List[Dict], str]:
        """Get Parquet files schema (placeholder)"""
        return False, [], "Parquet schema discovery not yet implemented"

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
    
    # Route to appropriate schema discovery method
    if connection.db_type.lower() == "sqlite3":
        if table_name:
            return SchemaDiscoveryService.get_sqlite_columns(config, table_name)
        else:
            return SchemaDiscoveryService.get_sqlite_tables(config)
    elif connection.db_type.lower() == "influxdb":
        return SchemaDiscoveryService.get_influxdb_measurements(config)
    elif connection.db_type.lower() == "parquet":
        return SchemaDiscoveryService.get_parquet_files(config)
    else:
        return False, {}, f"Unsupported database type: {connection.db_type}"