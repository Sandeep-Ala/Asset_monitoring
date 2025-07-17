# test_parquet_implementation.py - Test Script for Parquet Support

"""
Test script to validate Parquet implementation
Run this to test the new Parquet functionality
"""

import os
import sys
import pandas as pd
from services.connection_service import ConnectionTestService
from services.schema_discovery_service import SchemaDiscoveryService
import pandas as pd
import pyarrow as pa
def test_parquet_connection():
    """Test Parquet connection functionality"""
    print(" Testing Parquet Connection Implementation")
    print("=" * 50)
    
    # Test configuration
    test_config = {
        "base_path": r"D:/Asset Monitoring System/Data-Backup/site=UK_Tollgate"
    }
    
    print(f" Testing with base path: {test_config['base_path']}")
    
    # Test 1: Connection Testing
    print("\n Testing Parquet Connection...")
    success, message = ConnectionTestService.test_parquet_connection(test_config)
    print(f"   Result: {' SUCCESS' if success else ' FAILED'}")
    print(f"   Message: {message}")
    
    if not success:
        print("\n Connection test failed. Check your base path and parquet files.")
        return False
    
    # Test 2: Structure Analysis
    print("\n Testing Parquet Structure Analysis...")
    success, structure_info, message = ConnectionTestService.get_parquet_structure_info(test_config)
    print(f"   Result: {' SUCCESS' if success else ' FAILED'}")
    print(f"   Message: {message}")
    
    if success:
        print(f"    Found {structure_info['total_files']} parquet files")
        print(f"    Equipment types: {structure_info['equipment_types']}")
        print(f"    DCU values: {structure_info['dcu_values']}")
        print(f"    Sample files: {structure_info['sample_files'][:2]}")
    
    # Test 3: Schema Discovery - Tables
    print("\n Testing Parquet Tables Discovery...")
    test_config['db_type'] = 'parquet'  # Add db_type for schema discovery
    success, tables, message = SchemaDiscoveryService.get_parquet_tables(test_config)
    print(f"   Result: {'SUCCESS' if success else ' FAILED'}")
    print(f"   Message: {message}")
    
    if success:
        print(f"    Found {len(tables)} equipment tables:")
        for table in tables:
            print(f"      - {table['name']}: {table['row_count']} rows, {table['file_count']} files")
    
    # Test 4: Schema Discovery - Columns for first table
    if success and tables:
        print("\n Testing Parquet Columns Discovery...")
        first_table = tables[0]['name']
        success, columns, message = SchemaDiscoveryService.get_parquet_columns(test_config, first_table)
        print(f"   Result: {' SUCCESS' if success else ' FAILED'}")
        print(f"   Message: {message}")
        
        if success:
            print(f"   Found {len(columns)} columns for table '{first_table}':")
            
            # Separate partition and parquet columns
            partition_cols = [col for col in columns if col.get('is_partition', False)]
            parquet_cols = [col for col in columns if not col.get('is_partition', False)]
            
            print(f"     Partition columns ({len(partition_cols)}):")
            for col in partition_cols:
                print(f"      - {col['name']} ({col['data_type']}): {col['partition_values']}")
            
            print(f"   Parquet columns ({len(parquet_cols)}):")
            for col in parquet_cols[:5]:  # Show first 5
                print(f"      - {col['name']} ({col['data_type']}) -> {col['suggested_for']}")
            
            if len(parquet_cols) > 5:
                print(f"      ... and {len(parquet_cols) - 5} more columns")
    
    # Test 5: Complete Schema
    print("\n Testing Complete Schema Retrieval...")
    success, schema, message = SchemaDiscoveryService.get_complete_schema(test_config, quick_mode=True)
    print(f"   Result: {' SUCCESS' if success else ' FAILED'}")
    print(f"   Message: {message}")
    
    if success:
        db_info = schema['database_info']
        print(f"    Database Type: {db_info['type']}")
        print(f"    Total Tables: {db_info['total_tables']}")
        print(f"    Analysis Mode: {db_info['analysis_mode']}")
        
        # Show summary of first table
        if schema['tables']:
            first_table = schema['tables'][0]
            print(f"    First Table: {first_table['name']}")
            print(f"      - Total Columns: {first_table['total_columns']}")
            print(f"      - Partition Columns: {first_table.get('partition_columns', 0)}")
            print(f"      - Parquet Columns: {first_table.get('parquet_columns', 0)}")
            print(f"      - Column Types: {first_table.get('column_type_summary', {})}")
    
    print("\n Parquet implementation test completed!")
    return True

def create_sample_parquet_structure():
    """Create sample parquet files for testing (if needed)"""
    print(" Creating sample Parquet structure for testing...")
    
    base_path = r"D:\Asset Monitoring System\Data-Backup\site=UK_Tollgate_TEST"
    
    # Sample data structure
    sample_data = {
        'bms': {
            't_sampling_time': pd.date_range('2025-01-01', periods=100, freq='1min'),
            'voltage': [12.5 + i * 0.1 for i in range(100)],
            'current': [1.2 + i * 0.01 for i in range(100)],
            'temperature': [25.0 + i * 0.1 for i in range(100)],
            'soc': [80 + i * 0.1 for i in range(100)]
        },
        'rmu4': {
            't_sampling_time': pd.date_range('2025-01-01', periods=100, freq='1min'),
            'pressure': [1.0 + i * 0.01 for i in range(100)],
            'flow_rate': [10.0 + i * 0.1 for i in range(100)],
            'status': ['active'] * 100
        }
    }
    
    # Create directory structure and files
    for equipment, data in sample_data.items():
        for dcu in [1, 2]:
            dir_path = os.path.join(
                base_path, 
                "year=2025", 
                "month=01", 
                "day=01", 
                f"equipment={equipment}", 
                f"dcu={dcu}"
            )
            os.makedirs(dir_path, exist_ok=True)
            
            # Create DataFrame and save as parquet
            df = pd.DataFrame(data)
            file_path = os.path.join(dir_path, f"{equipment}.parquet")
            df.to_parquet(file_path, index=False)
            print(f"   Created: {file_path}")
    
    print(f" Sample structure created at: {base_path}")
    return base_path

if __name__ == "__main__":
    print(" Parquet Implementation Test Suite")
    print("=" * 50)
    
    # Check if pandas is available
    try:

        print(" Dependencies available: pandas, pyarrow")
        print(f"    pandas version: {pd.__version__}")
        print(f"    pyarrow version: {pa.__version__}")
        
        # Test parquet compatibility
        test_df = pd.DataFrame({'test': [1, 2, 3]})
        test_file = "temp_test.parquet"
        test_df.to_parquet(test_file, index=False)
        
        # Test reading
        try:
            df_read = pd.read_parquet(test_file)
            print(" Parquet read/write test successful")
        except Exception as e:
            print(f" Parquet compatibility issue: {e}")
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
    except Exception as e:
        print(e)
    
    # Option to create sample data
    create_sample = input("\n Create sample parquet files for testing? (y/n): ").lower().strip()
    if create_sample == 'y':
        sample_path = create_sample_parquet_structure()
        print(f"\n🔄 Update test_config['base_path'] to: {sample_path}")
    
    # Run tests
    test_parquet_connection()
    
    print("\n📋 Next Steps:")
    print("1. Install dependencies: pip install pandas pyarrow")
    print("2. Update your base_path in the test_config")
    print("3. Test with your actual parquet files")
    print("4. Use the frontend to test the complete integration")
    
    print("\n🌐 Frontend Testing:")
    print("- Go to http://localhost:9000/datasources")
    print("- Create a new Parquet connection")
    print("- Test the connection")
    print("- Discover schema")
    print("- Go to metadata mapping and test drag & drop")