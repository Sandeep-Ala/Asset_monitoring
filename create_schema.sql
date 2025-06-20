-- backend/create_datasource_schema.sql
-- SQL queries to create data source tables in MetaDB.sqlite3

-- 1. Data Sources table
CREATE TABLE data_sources (
    source_id TEXT PRIMARY KEY,
    source_name TEXT(128) NOT NULL,
    source_type TEXT(32) NOT NULL CHECK (source_type IN ('influxdb', 'parquet')),
    connection_config TEXT NOT NULL,  -- JSON string
    is_active BOOLEAN DEFAULT TRUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 2. Source Mappings table
CREATE TABLE source_mappings (
    mapping_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    equipment_id INTEGER NOT NULL,
    measurement_name TEXT(128) NOT NULL,
    tag_mappings TEXT,  -- JSON string: {"n_rack": "rack", "n_bank": "bank"}
    field_mappings TEXT, -- JSON string: {"n_soc": "soc", "n_soh": "soh"}
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (source_id) REFERENCES data_sources(source_id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipments(id) ON DELETE CASCADE
);

-- 3. Schema Cache table
CREATE TABLE schema_cache (
    cache_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    schema_type TEXT(32) NOT NULL CHECK (schema_type IN ('measurements', 'tags', 'fields')),
    schema_data TEXT NOT NULL,  -- JSON string
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (source_id) REFERENCES data_sources(source_id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_data_sources_type ON data_sources(source_type);
CREATE INDEX idx_data_sources_active ON data_sources(is_active);
CREATE INDEX idx_source_mappings_source ON source_mappings(source_id);
CREATE INDEX idx_source_mappings_equipment ON source_mappings(equipment_id);
CREATE INDEX idx_schema_cache_source ON schema_cache(source_id);
CREATE INDEX idx_schema_cache_type ON schema_cache(schema_type);
CREATE INDEX idx_schema_cache_expires ON schema_cache(expires_at);

-- Create triggers to automatically update updated_at timestamps
CREATE TRIGGER update_data_sources_timestamp 
    AFTER UPDATE ON data_sources
    FOR EACH ROW
BEGIN
    UPDATE data_sources SET updated_at = datetime('now') WHERE source_id = NEW.source_id;
END;

CREATE TRIGGER update_source_mappings_timestamp 
    AFTER UPDATE ON source_mappings
    FOR EACH ROW
BEGIN
    UPDATE source_mappings SET updated_at = datetime('now') WHERE mapping_id = NEW.mapping_id;
END;

-- Insert sample data (optional - for testing)
/*
INSERT INTO data_sources (source_id, source_name, source_type, connection_config, is_active) VALUES
('sample-influx-001', 'Main InfluxDB', 'influxdb', '{"url": "http://localhost:8086", "token": "your-token", "org": "your-org", "bucket": "equipment-data"}', TRUE),
('sample-parquet-001', 'Local Parquet Files', 'parquet', '{"base_path": "D:\\Asset Monitoring System\\Data-Backup\\site=UK_Tollgate", "path_pattern": "**/*.parquet"}', TRUE);
*/














--===========================================================================================================================

--1 pages
CREATE TABLE pages (
    page_id TEXT PRIMARY KEY,
    page_name TEXT NOT NULL,
    page_route TEXT NOT NULL,
    user_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
CREATE UNIQUE INDEX `sqlite_autoindex_pages_1` ON `pages` (page_id);

-- 2. Master Model
CREATE TABLE master_model (
    model_id INTEGER PRIMARY KEY NOT NULL,
    name TEXT(64) UNIQUE NOT NULL,
    enable INTEGER NOT NULL
);

-- 3. Equipments
CREATE TABLE equipments (
    id INTEGER PRIMARY KEY,
    name TEXT(64) UNIQUE,
    model_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    location TEXT(64),
    enable INTEGER NOT NULL,
    FOREIGN KEY (model_id) REFERENCES master_model(model_id)
);

-- 4. Equipment Specifications
CREATE TABLE equipment_specs (
    id INTEGER PRIMARY KEY,
    eqp_id INTEGER,
    key TEXT(64) NOT NULL,
    value TEXT(64) NOT NULL,
    desc TEXT(64),
    unit TEXT(64),
    enable INTEGER NOT NULL,
    FOREIGN KEY (eqp_id) REFERENCES equipments(id)
);

-- 5. Equipment Signals
CREATE TABLE equipment_signals (
    id INTEGER PRIMARY KEY,
    eqp_id INTEGER NOT NULL,
    key TEXT(64) NOT NULL,
    value TEXT(64),
    unit TEXT(64),
    desc TEXT(64),
    enable INTEGER NOT NULL,
    FOREIGN KEY (eqp_id) REFERENCES equipments(id)
);

-- 6. Equipment Documents
CREATE TABLE equipment_doc (
    id INTEGER PRIMARY KEY,
    eqp_id INTEGER NOT NULL,
    path TEXT(128),
    desc TEXT(64),
    FOREIGN KEY (eqp_id) REFERENCES equipments(id)
);

-- 7. Equipment Filters (Dynamic "where clause" support)
CREATE TABLE equipment_filters (
    id INTEGER PRIMARY KEY,
    eqp_id INTEGER NOT NULL,
    filter_key TEXT(64) NOT NULL,
    filter_value TEXT(64) NOT NULL,
    FOREIGN KEY (eqp_id) REFERENCES equipments(id)
);


