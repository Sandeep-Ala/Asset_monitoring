# services/schema_discovery_service.py - Updated with Parquet Implementation

import sqlite3
import os
import glob
import pandas as pd
from typing import List, Dict, Tuple, Optional, Set
from sqlalchemy.orm import Session
import services.datasource_crud as crud
from collections import defaultdict

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
    
    # ---------- PARQUET IMPLEMENTATION ----------
    
    @staticmethod
    def get_parquet_tables(config: Dict[str, str]) -> Tuple[bool, List[Dict], str]:
        """Get all unique equipment tables from Parquet directory structure"""
        try:
            base_path = config.get('base_path')
            if not base_path or not os.path.exists(base_path):
                return False, [], "Base path not found"
            
            # Discover all parquet files
            all_files = SchemaDiscoveryService._discover_all_parquet_files(base_path)
            
            if not all_files:
                return False, [], "No parquet files found in directory structure"
            
            # Group files by equipment type
            equipment_files = defaultdict(list)
            
            for file_path in all_files:
                equipment_name = SchemaDiscoveryService._extract_equipment_from_path(file_path)
                if equipment_name:
                    equipment_files[equipment_name].append(file_path)
            
            if not equipment_files:
                return False, [], "No valid equipment partitions found"
            
            # Create table information for each equipment type
            tables = []
            for equipment_name, files in equipment_files.items():
                try:
                    # Read a sample file to get basic info (compatibility fix)
                    sample_file = files[0]
                    try:
                        # Try pyarrow first for better performance
                        import pyarrow.parquet as pq
                        parquet_file = pq.ParquetFile(sample_file)
                        column_count = len(parquet_file.schema_arrow)
                    except Exception:
                        # Fallback to pandas
                        df_sample = pd.read_parquet(sample_file)
                        if len(df_sample) > 0:
                            df_sample = df_sample.head(1)  # Take first row only
                        column_count = len(df_sample.columns)
                    
                    # Estimate total rows across all dates (approximate)
                    estimated_rows = len(files) * 1000  # Rough estimate
                    
                    table_info = {
                        "name": equipment_name,
                        "type": "parquet_table",
                        "row_count": f"~{estimated_rows:,}",
                        "file_count": len(files),
                        "sample_file": sample_file,
                        "parquet_columns": column_count,
                        "base_path": base_path
                    }
                    
                    tables.append(table_info)
                    
                except Exception as e:
                    print(f"Error processing {equipment_name}: {str(e)}")
                    continue
            
            # Sort tables by name
            tables.sort(key=lambda x: x["name"])
            
            return True, tables, f"Found {len(tables)} equipment tables from {len(all_files)} parquet files"
            
        except Exception as e:
            return False, [], f"Error discovering parquet tables: {str(e)}"
    
    @staticmethod
    def get_parquet_columns(config: Dict[str, str], table_name: str, quick_mode: bool = False) -> Tuple[bool, List[Dict], str]:
        """Get columns for a specific parquet table (equipment type)"""
        try:
            base_path = config.get('base_path')
            if not base_path or not os.path.exists(base_path):
                return False, [], "Base path not found"
            
            # Find files for this equipment
            equipment_files = SchemaDiscoveryService._find_equipment_files(base_path, table_name)
            
            if not equipment_files:
                return False, [], f"No parquet files found for equipment '{table_name}'"
            
            # Read schema from a representative file (compatibility fix)
            sample_file = equipment_files[0]
            try:
                # Method 1: Try pandas without nrows parameter
                df_sample = pd.read_parquet(sample_file)
                if not quick_mode and len(df_sample) > 100:
                    df_sample = df_sample.head(100)  # Limit to 100 rows for analysis
                elif quick_mode and len(df_sample) > 1:
                    df_sample = df_sample.head(1)   # Just 1 row for quick mode
            except Exception as e:
                return False, [], f"Error reading parquet file {sample_file}: {str(e)}"
            
            # Get partition information
            partition_info = SchemaDiscoveryService._extract_partition_info(equipment_files)
            
            columns = []
            
            # Add partition columns as filter columns
            for partition_col, values in partition_info.items():
                if partition_col not in ['year', 'month', 'day']:  # Skip timeline partitions
                    column_data = {
                        "name": partition_col,
                        "data_type": "partition_string",
                        "nullable": False,
                        "primary_key": False,
                        "default_value": None,
                        "total_rows": len(equipment_files),
                        "distinct_count": len(values),
                        "distinctness_ratio": len(values) / len(equipment_files) if equipment_files else 0,
                        "sample_values": list(values)[:3],
                        "category": "categorical_text",
                        "suggested_for": ["filters"],
                        "is_partition": True,
                        "partition_values": sorted(list(values))
                    }
                    columns.append(column_data)
            
            # Add parquet file columns
            for col_name in df_sample.columns:
                col_dtype = str(df_sample[col_name].dtype)
                
                if quick_mode:
                    # Quick analysis
                    column_data = {
                        "name": col_name,
                        "data_type": col_dtype,
                        "nullable": True,
                        "primary_key": False,
                        "default_value": None,
                        "total_rows": "~1M+",
                        "distinct_count": "Not analyzed",
                        "distinctness_ratio": 0,
                        "sample_values": [],
                        "category": SchemaDiscoveryService._classify_parquet_column_simple(col_name, col_dtype),
                        "suggested_for": SchemaDiscoveryService._get_parquet_suggested_usage(col_name, col_dtype),
                        "is_partition": False
                    }
                else:
                    # Detailed analysis
                    sample_values = df_sample[col_name].dropna().astype(str).tolist()[:3]
                    non_null_count = df_sample[col_name].notna().sum()
                    distinct_count = df_sample[col_name].nunique()
                    
                    distinctness_ratio = distinct_count / len(df_sample) if len(df_sample) > 0 else 0
                    
                    category = SchemaDiscoveryService._classify_parquet_column(col_name, col_dtype, distinctness_ratio, sample_values)
                    
                    column_data = {
                        "name": col_name,
                        "data_type": col_dtype,
                        "nullable": non_null_count < len(df_sample),
                        "primary_key": False,
                        "default_value": None,
                        "total_rows": f"~{len(equipment_files) * 1000:,}",
                        "distinct_count": distinct_count,
                        "distinctness_ratio": round(distinctness_ratio, 3),
                        "sample_values": sample_values,
                        "category": category,
                        "suggested_for": SchemaDiscoveryService._get_suggested_usage(category, distinctness_ratio),
                        "is_partition": False
                    }
                
                columns.append(column_data)
            
            message = f"Retrieved {len(columns)} columns for {table_name}"
            if quick_mode:
                message += " (quick mode)"
            
            return True, columns, message
            
        except Exception as e:
            return False, [], f"Error getting parquet columns: {str(e)}"
    
    @staticmethod
    def _discover_all_parquet_files(base_path: str) -> List[str]:
        """Discover all parquet files in the directory structure"""
        try:
            # Search pattern: base_path/**/equipment=*/dcu=*/*.parquet
            search_pattern = os.path.join(base_path, "**", "equipment=*", "dcu=*", "*.parquet")
            return glob.glob(search_pattern, recursive=True)
        except Exception as e:
            print(f"Error discovering files: {str(e)}")
            return []
    
    @staticmethod
    def _extract_equipment_from_path(file_path: str) -> Optional[str]:
        """Extract equipment name from file path"""
        try:
            # Split path and look for equipment= folder
            path_parts = file_path.split(os.sep)
            for part in path_parts:
                if part.startswith("equipment="):
                    return part.split("=")[1]
            return None
        except Exception:
            return None
    
    @staticmethod
    def _find_equipment_files(base_path: str, equipment_name: str) -> List[str]:
        """Find all files for a specific equipment"""
        try:
            search_pattern = os.path.join(base_path, "**", f"equipment={equipment_name}", "dcu=*", f"{equipment_name}.parquet")
            return glob.glob(search_pattern, recursive=True)
        except Exception:
            return []
    
    @staticmethod
    def _extract_partition_info(file_paths: List[str]) -> Dict[str, Set[str]]:
        """Extract partition information from file paths"""
        partition_info = defaultdict(set)
        
        for file_path in file_paths:
            # Split path and extract partition key=value pairs
            path_parts = file_path.split(os.sep)
            for part in path_parts:
                if "=" in part:
                    key, value = part.split("=", 1)
                    partition_info[key].add(value)
        
        return dict(partition_info)
    
    @staticmethod
    def _classify_parquet_column_simple(col_name: str, col_dtype: str) -> str:
        """Simple column classification for parquet columns"""
        name_lower = col_name.lower()
        dtype_lower = col_dtype.lower()
        
        # Time-related columns
        if any(keyword in name_lower for keyword in ['time', 'date', 'timestamp', 'created', 'updated']):
            return "timestamp"
        
        # Numeric columns
        if any(dtype in dtype_lower for dtype in ['int', 'float', 'double', 'decimal']):
            if any(keyword in name_lower for keyword in ['id', '_id', 'count', 'index']):
                return "identifier"
            return "numeric"
        
        # Boolean columns
        if 'bool' in dtype_lower:
            return "boolean"
        
        # String/object columns
        if any(dtype in dtype_lower for dtype in ['object', 'string', 'category']):
            return "text"
        
        return "unknown"
    
    @staticmethod
    def _classify_parquet_column(col_name: str, col_dtype: str, distinctness_ratio: float, sample_values: List[str]) -> str:
        """Detailed column classification for parquet columns"""
        name_lower = col_name.lower()
        dtype_lower = col_dtype.lower()
        
        # Time-related columns
        if any(keyword in name_lower for keyword in ['time', 'date', 'timestamp', 'created', 'updated']):
            return "timestamp"
        
        # ID columns
        if any(keyword in name_lower for keyword in ['id', '_id', 'uuid', 'key']) or distinctness_ratio > 0.9:
            return "identifier"
        
        # Boolean columns
        if 'bool' in dtype_lower or all(val in ['0', '1', 'true', 'false', 'True', 'False'] for val in sample_values if val):
            return "boolean"
        
        # Numeric columns
        if any(dtype in dtype_lower for dtype in ['int', 'float', 'double', 'decimal']):
            if distinctness_ratio < 0.1:
                return "categorical_numeric"
            return "numeric"
        
        # String columns
        if any(dtype in dtype_lower for dtype in ['object', 'string', 'category']):
            if distinctness_ratio < 0.1:
                return "categorical_text"
            return "text"
        
        return "unknown"
    
    @staticmethod
    def _get_parquet_suggested_usage(col_name: str, col_dtype: str) -> List[str]:
        """Get suggested usage for parquet columns"""
        name_lower = col_name.lower()
        dtype_lower = col_dtype.lower()
        
        # Time columns
        if any(keyword in name_lower for keyword in ['time', 'date', 'timestamp']):
            return ["timestamp_field"]
        
        # Numeric columns - likely signals
        if any(dtype in dtype_lower for dtype in ['int', 'float', 'double', 'decimal']):
            if any(keyword in name_lower for keyword in ['voltage', 'current', 'temperature', 'pressure', 'power', 'energy', 'soc', 'soh']):
                return ["signals", "specs"]
            return ["signals"]
        
        # Boolean columns
        if 'bool' in dtype_lower:
            return ["signals", "specs"]
        
        # String columns
        return ["specs", "documentation"]
    
    # ---------- EXISTING METHODS ----------
    
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
        
        return "unknown"
    
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
    
    @staticmethod
    def get_complete_schema(config: Dict[str, str], quick_mode: bool = True) -> Tuple[bool, Dict, str]:
        """Get complete database schema information with performance optimization"""
        try:
            db_type = config.get('db_type', 'sqlite3')
            
            if db_type.lower() == 'sqlite3':
                # SQLite implementation (existing)
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
            
            elif db_type.lower() == 'parquet':
                # Parquet implementation (new)
                success, tables, message = SchemaDiscoveryService.get_parquet_tables(config)
                if not success:
                    return False, {}, message
                
                schema = {
                    "database_info": {
                        "type": "parquet",
                        "base_path": config.get('base_path'),
                        "total_tables": len(tables),
                        "analysis_mode": "quick" if quick_mode else "full"
                    },
                    "tables": []
                }
                
                # Get columns for each equipment table
                for i, table in enumerate(tables):
                    print(f"Analyzing parquet table {i+1}/{len(tables)}: {table['name']}")
                    
                    success, columns, _ = SchemaDiscoveryService.get_parquet_columns(
                        config, table["name"], quick_mode=quick_mode
                    )
                    if success:
                        table["columns"] = columns
                        table["total_columns"] = len(columns)
                        
                        # Add column type summary
                        column_types = {}
                        partition_columns = 0
                        parquet_columns = 0
                        
                        for col in columns:
                            col_type = col["category"]
                            column_types[col_type] = column_types.get(col_type, 0) + 1
                            
                            if col.get("is_partition", False):
                                partition_columns += 1
                            else:
                                parquet_columns += 1
                        
                        table["column_type_summary"] = column_types
                        table["partition_columns"] = partition_columns
                        table["parquet_columns"] = parquet_columns
                    
                    schema["tables"].append(table)
                
                return True, schema, f"Parquet schema retrieved successfully from {config.get('base_path')}"
            
            else:
                return False, {}, f"Unsupported database type: {db_type}"
            
        except Exception as e:
            return False, {}, f"Error retrieving schema: {str(e)}"
    
    # Placeholder methods for future database types
    @staticmethod
    def get_influxdb_measurements(config: Dict[str, str]) -> Tuple[bool, List[Dict], str]:
        """Get InfluxDB measurements (placeholder)"""
        return False, [], "InfluxDB schema discovery not yet implemented"

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
    
    # Add db_type to config for schema discovery
    config['db_type'] = connection.db_type
    
    # Route to appropriate schema discovery method
    if connection.db_type.lower() == "sqlite3":
        if table_name:
            return SchemaDiscoveryService.get_sqlite_columns(config, table_name)
        else:
            return SchemaDiscoveryService.get_sqlite_tables(config)
    elif connection.db_type.lower() == "parquet":
        if table_name:
            return SchemaDiscoveryService.get_parquet_columns(config, table_name)
        else:
            return SchemaDiscoveryService.get_parquet_tables(config)
    elif connection.db_type.lower() == "influxdb":
        return SchemaDiscoveryService.get_influxdb_measurements(config)
    else:
        return False, {}, f"Unsupported database type: {connection.db_type}"