# standalone_parquet_test.py - Fixed Implementation Test

"""
Standalone test with fixed parquet implementation
This bypasses import issues and tests the functionality directly
"""

import os
import glob
import pandas as pd
from typing import Dict, Tuple, List, Set, Optional
from collections import defaultdict
import pyarrow.parquet as pq
import pyarrow

class FixedConnectionTestService:
    """Fixed version of connection test service"""
    
    @staticmethod
    def test_parquet_connection(config: Dict[str, str]) -> Tuple[bool, str]:
        """Test Parquet files connection - FIXED VERSION"""
        try:
            base_path = config.get('base_path')
            if not base_path:
                return False, "Base path is required for Parquet connection"
            
            # Check if directory exists
            if not os.path.exists(base_path):
                return False, f"Directory not found at path: {base_path}"
            
            if not os.path.isdir(base_path):
                return False, f"Path is not a directory: {base_path}"
            
            # Try to find parquet files with the expected structure
            parquet_files = FixedConnectionTestService._discover_parquet_files(base_path)
            
            if not parquet_files:
                return False, "No parquet files found in the specified directory structure"
            
            # Try to read schema from one file to validate it's a valid parquet - FIXED
            try:
                sample_file = parquet_files[0]
                
                # FIXED: Use pyarrow for schema reading first (faster and more compatible)
                try:
                    parquet_file = pq.ParquetFile(sample_file)
                    schema = parquet_file.schema_arrow
                    column_count = len(schema)
                    
                    return True, f"Parquet connection successful. Found {len(parquet_files)} parquet files with {column_count} columns in sample file."
                    
                except Exception:
                    # FIXED: Fallback to pandas without nrows parameter
                    df_sample = pd.read_parquet(sample_file)
                    if len(df_sample) > 0:
                        df_sample = df_sample.head(1)  # Take just first row
                    
                    return True, f"Parquet connection successful. Found {len(parquet_files)} parquet files with {len(df_sample.columns)} columns in sample file."
                    
            except Exception as e:
                return False, f"Failed to read parquet file: {str(e)}"
            
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def _discover_parquet_files(base_path: str, limit: int = 100) -> List[str]:
        """Discover parquet files in the directory structure"""
        parquet_files = []
        
        try:
            # Search pattern for parquet files in partitioned structure
            search_pattern = os.path.join(base_path, "**", "equipment=*", "dcu=*", "*.parquet")
            
            # Use glob to find all matching files
            found_files = glob.glob(search_pattern, recursive=True)
            
            # Limit results for performance during connection testing
            parquet_files = found_files[:limit]
            
            return parquet_files
            
        except Exception as e:
            print(f"Error discovering parquet files: {str(e)}")
            return []
    
    @staticmethod
    def get_parquet_structure_info(config: Dict[str, str]) -> Tuple[bool, Dict, str]:
        """Get basic structure information about parquet files"""
        try:
            base_path = config.get('base_path')
            if not base_path or not os.path.exists(base_path):
                return False, {}, "Invalid base path"
            
            # Discover all parquet files
            all_files = FixedConnectionTestService._discover_parquet_files(base_path, limit=1000)
            
            if not all_files:
                return False, {}, "No parquet files found"
            
            # Extract unique equipment types and dcu values
            equipment_types = set()
            dcu_values = set()
            
            for file_path in all_files:
                # Extract equipment and dcu from path
                path_parts = file_path.replace(base_path, "").split(os.sep)
                
                for part in path_parts:
                    if part.startswith("equipment="):
                        equipment_types.add(part.split("=")[1])
                    elif part.startswith("dcu="):
                        dcu_values.add(part.split("=")[1])
            
            structure_info = {
                "total_files": len(all_files),
                "equipment_types": sorted(list(equipment_types)),
                "dcu_values": sorted(list(dcu_values)),
                "base_path": base_path,
                "sample_files": all_files[:5]  # First 5 files as samples
            }
            
            return True, structure_info, "Structure analysis completed"
            
        except Exception as e:
            return False, {}, f"Error analyzing structure: {str(e)}"

class FixedSchemaDiscoveryService:
    """Fixed version of schema discovery service"""
    
    @staticmethod
    def get_parquet_tables(config: Dict[str, str]) -> Tuple[bool, List[Dict], str]:
        """Get all unique equipment tables from Parquet directory structure - FIXED"""
        try:
            base_path = config.get('base_path')
            if not base_path or not os.path.exists(base_path):
                return False, [], "Base path not found"
            
            # Discover all parquet files
            all_files = FixedSchemaDiscoveryService._discover_all_parquet_files(base_path)
            
            if not all_files:
                return False, [], "No parquet files found in directory structure"
            
            # Group files by equipment type
            equipment_files = defaultdict(list)
            
            for file_path in all_files:
                equipment_name = FixedSchemaDiscoveryService._extract_equipment_from_path(file_path)
                if equipment_name:
                    equipment_files[equipment_name].append(file_path)
            
            if not equipment_files:
                return False, [], "No valid equipment partitions found"
            
            # Create table information for each equipment type
            tables = []
            for equipment_name, files in equipment_files.items():
                try:
                    # FIXED: Read a sample file to get basic info (compatibility fix)
                    sample_file = files[0]
                    try:
                        # Try pyarrow first for better performance
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
        """Get columns for a specific parquet table (equipment type) - FIXED"""
        try:
            base_path = config.get('base_path')
            if not base_path or not os.path.exists(base_path):
                return False, [], "Base path not found"
            
            # Find files for this equipment
            equipment_files = FixedSchemaDiscoveryService._find_equipment_files(base_path, table_name)
            
            if not equipment_files:
                return False, [], f"No parquet files found for equipment '{table_name}'"
            
            # FIXED: Read schema from a representative file (compatibility fix)
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
            partition_info = FixedSchemaDiscoveryService._extract_partition_info(equipment_files)
            
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
                        "category": FixedSchemaDiscoveryService._classify_parquet_column_simple(col_name, col_dtype),
                        "suggested_for": FixedSchemaDiscoveryService._get_parquet_suggested_usage(col_name, col_dtype),
                        "is_partition": False
                    }
                else:
                    # Detailed analysis
                    sample_values = df_sample[col_name].dropna().astype(str).tolist()[:3]
                    non_null_count = df_sample[col_name].notna().sum()
                    distinct_count = df_sample[col_name].nunique()
                    
                    distinctness_ratio = distinct_count / len(df_sample) if len(df_sample) > 0 else 0
                    
                    category = FixedSchemaDiscoveryService._classify_parquet_column(col_name, col_dtype, distinctness_ratio, sample_values)
                    
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
                        "suggested_for": FixedSchemaDiscoveryService._get_suggested_usage(category, distinctness_ratio),
                        "is_partition": False
                    }
                
                columns.append(column_data)
            
            message = f"Retrieved {len(columns)} columns for {table_name}"
            if quick_mode:
                message += " (quick mode)"
            
            return True, columns, message
            
        except Exception as e:
            return False, [], f"Error getting parquet columns: {str(e)}"
    
    # Helper methods
    @staticmethod
    def _discover_all_parquet_files(base_path: str) -> List[str]:
        """Discover all parquet files in the directory structure"""
        try:
            search_pattern = os.path.join(base_path, "**", "equipment=*", "dcu=*", "*.parquet")
            return glob.glob(search_pattern, recursive=True)
        except Exception as e:
            print(f"Error discovering files: {str(e)}")
            return []
    
    @staticmethod
    def _extract_equipment_from_path(file_path: str) -> Optional[str]:
        """Extract equipment name from file path"""
        try:
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

def test_fixed_parquet_implementation():
    """Test the fixed parquet implementation"""
    print(" Testing FIXED Parquet Implementation")
    print("=" * 50)
    
    # Test configuration
    test_config = {
        "base_path": r"D:\Asset Monitoring System\Data-Backup\site=UK_Tollgate"
    }
    
    print(f" Testing with base path: {test_config['base_path']}")
    
    # Test 1: Connection Testing
    print("\n1️ Testing Fixed Parquet Connection...")
    success, message = FixedConnectionTestService.test_parquet_connection(test_config)
    print(f"   Result: {' SUCCESS' if success else ' FAILED'}")
    print(f"   Message: {message}")
    
    if not success:
        print("\n Connection test failed. Check your base path and parquet files.")
        return False
    
    # Test 2: Structure Analysis
    print("\n Testing Fixed Structure Analysis...")
    success, structure_info, message = FixedConnectionTestService.get_parquet_structure_info(test_config)
    print(f"   Result: {' SUCCESS' if success else ' FAILED'}")
    print(f"   Message: {message}")
    
    if success:
        print(f"    Found {structure_info['total_files']} parquet files")
        print(f"    Equipment types: {structure_info['equipment_types']}")
        print(f"    DCU values: {structure_info['dcu_values']}")
    
    # Test 3: Tables Discovery
    print("\n3 Testing Fixed Tables Discovery...")
    success, tables, message = FixedSchemaDiscoveryService.get_parquet_tables(test_config)
    print(f"   Result: {' SUCCESS' if success else ' FAILED'}")
    print(f"   Message: {message}")
    
    if success:
        print(f"    Found {len(tables)} equipment tables:")
        for table in tables[:5]:  # Show first 5
            print(f"      - {table['name']}: {table['row_count']} rows, {table['file_count']} files")
        if len(tables) > 5:
            print(f"      ... and {len(tables) - 5} more tables")
    
    # Test 4: Columns Discovery for first table
    if success and tables:
        print("\n Testing Fixed Columns Discovery...")
        first_table = tables[0]['name']
        success, columns, message = FixedSchemaDiscoveryService.get_parquet_columns(test_config, first_table, quick_mode=True)
        print(f"   Result: {' SUCCESS' if success else ' FAILED'}")
        print(f"   Message: {message}")
        
        if success:
            partition_cols = [col for col in columns if col.get('is_partition', False)]
            parquet_cols = [col for col in columns if not col.get('is_partition', False)]
            
            print(f"     Partition columns ({len(partition_cols)}):")
            for col in partition_cols:
                print(f"      - {col['name']}: {col['partition_values']}")
            
            print(f"    First 5 parquet columns (of {len(parquet_cols)}):")
            for col in parquet_cols[:5]:
                print(f"      - {col['name']} ({col['data_type']}) → {col['suggested_for']}")
    
    print("\n Fixed implementation test completed!")
    return True

if __name__ == "__main__":
    print(" Fixed Parquet Implementation Test")
    print("=" * 50)
    
    try:
        print(f"📦 pandas: {pd.__version__}")
        print(f"📦 pyarrow: {pyarrow.__version__}")
        
        test_fixed_parquet_implementation()
        
        print("\n📋 Next Steps:")
        print("1. If this test passes, the backend is ready")
        print("2. Start the server: uvicorn main:app --reload --port 8000")
        print("3. Test frontend integration at /datasources")
        
    except Exception as e:
        print(e)