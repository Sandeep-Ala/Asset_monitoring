# backend/quick_fix.py
import sqlite3
import os

def fix_database():
    """Quick fix for database issues"""
    db_path = "D:/Asset Monitoring System/GITHUB/Asset_monitoring/MetaDB.sqlite3"
    
    # Ensure database exists
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Fixing database tables...")
        
        # Drop and recreate data source tables with correct schema
        cursor.execute("DROP TABLE IF EXISTS schema_cache;")
        cursor.execute("DROP TABLE IF EXISTS source_mappings;")
        cursor.execute("DROP TABLE IF EXISTS data_sources;")
        
        # Create data_sources table
        cursor.execute("""
        CREATE TABLE data_sources (
            source_id TEXT PRIMARY KEY,
            source_name TEXT(128) NOT NULL,
            source_type TEXT(32) NOT NULL,
            connection_config TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """)
        
        # Create source_mappings table
        cursor.execute("""
        CREATE TABLE source_mappings (
            mapping_id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            equipment_id INTEGER NOT NULL,
            measurement_name TEXT(128) NOT NULL,
            tag_mappings TEXT,
            field_mappings TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (source_id) REFERENCES data_sources(source_id),
            FOREIGN KEY (equipment_id) REFERENCES equipments(id)
        );
        """)
        
        # Create schema_cache table
        cursor.execute("""
        CREATE TABLE schema_cache (
            cache_id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            schema_type TEXT(32) NOT NULL,
            schema_data TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (source_id) REFERENCES data_sources(source_id)
        );
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_data_sources_type ON data_sources(source_type);")
        cursor.execute("CREATE INDEX idx_source_mappings_source ON source_mappings(source_id);")
        cursor.execute("CREATE INDEX idx_schema_cache_source ON schema_cache(source_id);")
        
        conn.commit()
        print("✅ Database tables fixed successfully!")
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%source%';")
        tables = cursor.fetchall()
        print(f"Created tables: {[t[0] for t in tables]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    fix_database()