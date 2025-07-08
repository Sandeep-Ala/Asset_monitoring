# quick_parquet_test.py - Simple Compatibility Test

"""
Quick test to verify Parquet implementation compatibility
"""

import os
import glob
import pandas as pd

def quick_test():
    """Quick test of parquet functionality"""
    print("🧪 Quick Parquet Compatibility Test")
    print("=" * 40)
    
    # Test path
    base_path = r"D:/Asset Monitoring System/Data-Backup/site=UK_Tollgate"
    print(f"📁 Base path: {base_path}")
    
    # Check if directory exists
    if not os.path.exists(base_path):
        print(f"❌ Directory not found: {base_path}")
        return False
    
    print("✅ Directory exists")
    
    # Find parquet files
    print("\n🔍 Searching for parquet files...")
    search_pattern = os.path.join(base_path, "**", "equipment=*", "dcu=*", "*.parquet")
    files = glob.glob(search_pattern, recursive=True)
    
    print(f"📄 Found {len(files)} parquet files")
    
    if not files:
        print("❌ No parquet files found with expected structure")
        print("Expected pattern: equipment=*/dcu=*/*.parquet")
        return False
    
    # Show first few files
    print("📋 Sample files:")
    for i, file in enumerate(files[:3]):
        print(f"   {i+1}. {file}")
    
    # Test reading one file
    print(f"\n📖 Testing file read: {files[0]}")
    try:
        # Read without nrows parameter
        df = pd.read_parquet(files[0])
        print(f"✅ Successfully read parquet file")
        print(f"   📊 Shape: {df.shape}")
        print(f"   📈 Columns: {list(df.columns)[:5]}{'...' if len(df.columns) > 5 else ''}")
        
        # Test with head() instead of nrows
        df_sample = df.head(1)
        print(f"   🔢 Sample shape: {df_sample.shape}")
        
    except Exception as e:
        print(f"❌ Error reading parquet file: {e}")
        return False
    
    # Extract equipment and dcu info
    print(f"\n🏭 Analyzing structure...")
    equipment_types = set()
    dcu_values = set()
    
    for file_path in files:
        path_parts = file_path.replace(base_path, "").split(os.sep)
        for part in path_parts:
            if part.startswith("equipment="):
                equipment_types.add(part.split("=")[1])
            elif part.startswith("dcu="):
                dcu_values.add(part.split("=")[1])
    
    print(f"   🏭 Equipment types: {sorted(list(equipment_types))}")
    print(f"   🔢 DCU values: {sorted(list(dcu_values))}")
    
    print("\n✅ Quick test completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the backend server: uvicorn main:app --reload --port 8000")
    print("2. Test Parquet connection in frontend")
    
    return True

if __name__ == "__main__":
    try:
        import pandas as pd
        import pyarrow
        print(f"📦 pandas: {pd.__version__}")
        print(f"📦 pyarrow: {pyarrow.__version__}")
        
        quick_test()
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install pandas pyarrow")