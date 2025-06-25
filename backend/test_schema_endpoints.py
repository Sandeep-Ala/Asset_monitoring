# test_schema_endpoints.py
# Test script for Phase 1.2 - Schema Discovery APIs

import requests
import json

BASE_URL = "http://localhost:8000"

def test_schema_discovery():
    """Test script for schema discovery endpoints"""
    
    print("=== Testing Schema Discovery APIs ===\n")
    
    # Step 1: Create a test connection
    print("1. Creating test SQLite connection...")
    connection_data = {
        "name": "Test Schema Discovery-2",
        "db_type": "sqlite3", 
        "description": "Testing schema discovery functionality"
    }
    
    response = requests.post(f"{BASE_URL}/datasources/connections", json=connection_data)
    if response.status_code == 200:
        connection = response.json()
        connection_id = connection["id"]
        print(f"✅ Connection created: {connection_id}")
    else:
        print(f"❌ Failed to create connection: {response.text}")
        return
    
    # Step 2: Test the connection
    print("\n2. Testing connection...")
    test_data = {
        "connection_id": connection_id,
        "config": {
            "database_path": "D:/Asset Monitoring System/Data-Backup/DCU_11_20250527.sqlite3"  # Update this path
        }
    }
    
    response = requests.post(f"{BASE_URL}/datasources/connections/test", json=test_data)
    if response.status_code == 200 and response.json()["success"]:
        print("✅ Connection test successful")
    else:
        print(f"❌ Connection test failed: {response.text}")
        return
    
    # Step 3: Get tables
    print("\n3. Getting tables...")
    response = requests.get(f"{BASE_URL}/datasources/connections/{connection_id}/tables")
    if response.status_code == 200:
        tables_response = response.json()
        if tables_response["success"]:
            tables = tables_response["data"]
            print(f"✅ Found {len(tables)} tables:")
            for table in tables[:5]:  # Show first 5 tables
                print(f"   - {table['name']} ({table['row_count']} rows)")
            
            # Step 4: Get columns for first table
            if tables:
                table_name = tables[0]["name"]
                print(f"\n4. Getting columns for table '{table_name}'...")
                response = requests.get(f"{BASE_URL}/datasources/connections/{connection_id}/tables/{table_name}/columns")
                if response.status_code == 200:
                    columns_response = response.json()
                    if columns_response["success"]:
                        columns = columns_response["data"]
                        print(f"✅ Found {len(columns)} columns:")
                        for col in columns[:5]:  # Show first 5 columns
                            print(f"   - {col['name']} ({col['data_type']}) - Category: {col['category']}, Suggested: {col['suggested_for']}")
                    else:
                        print(f"❌ Failed to get columns: {columns_response['message']}")
                else:
                    print(f"❌ Failed to get columns: {response.text}")
        else:
            print(f"❌ Failed to get tables: {tables_response['message']}")
    else:
        print(f"❌ Failed to get tables: {response.text}")
    
    # Step 5: Get complete schema
    print(f"\n5. Getting complete schema...")
    response = requests.get(f"{BASE_URL}/datasources/connections/{connection_id}/schema")
    if response.status_code == 200:
        schema_response = response.json()
        if schema_response["success"]:
            schema = schema_response["data"]
            print(f"✅ Complete schema retrieved:")
            print(f"   - Database: {schema['database_info']['type']}")
            print(f"   - Total tables: {schema['database_info']['total_tables']}")
            for table in schema["tables"][:3]:  # Show first 3 tables with details
                print(f"   - Table: {table['name']} ({table['total_columns']} columns)")
                if 'column_type_summary' in table:
                    print(f"     Column types: {table['column_type_summary']}")
        else:
            print(f"❌ Failed to get schema: {schema_response['message']}")
    else:
        print(f"❌ Failed to get schema: {response.text}")
    
    # Step 6: Get quick info
    print(f"\n6. Getting quick connection info...")
    response = requests.get(f"{BASE_URL}/datasources/connections/{connection_id}/quick-info")
    if response.status_code == 200:
        quick_info = response.json()
        print(f"✅ Quick info retrieved:")
        print(f"   - Connection: {quick_info['connection']['name']}")
        print(f"   - Status: {quick_info['connection']['status']}")
        if 'stats' in quick_info:
            print(f"   - Stats: {quick_info['stats']}")
    else:
        print(f"❌ Failed to get quick info: {response.text}")
    
    print(f"\n=== Schema Discovery Testing Complete ===")
    print(f"Connection ID for further testing: {connection_id}")

if __name__ == "__main__":
    test_schema_discovery()