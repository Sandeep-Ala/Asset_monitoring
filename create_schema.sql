CREATE TABLE pages (
    page_id TEXT PRIMARY KEY,
    page_name TEXT NOT NULL,
    page_route TEXT NOT NULL,
    user_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)

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


CREATE TABLE connection_configs (
	id INTEGER NOT NULL, 
	connection_id VARCHAR NOT NULL, 
	config_key VARCHAR(64) NOT NULL, 
	config_value TEXT NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(connection_id) REFERENCES data_connections (id)
)

CREATE TABLE data_connections (
	id VARCHAR NOT NULL, 
	name VARCHAR(128) NOT NULL, 
	db_type VARCHAR(32) NOT NULL, 
	description TEXT, 
	status VARCHAR(32), 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (name)
)
CREATE UNIQUE INDEX `sqlite_autoindex_data_connections_2` ON `data_connections` (name);
CREATE UNIQUE INDEX `sqlite_autoindex_data_connections_1` ON `data_connections` (id);




-- Enhanced pages table
ALTER TABLE pages ADD COLUMN layout_data TEXT;

-- New widget table
CREATE TABLE widgets (
    widget_id TEXT PRIMARY KEY,
    page_id TEXT,
    widget_type TEXT,
    widget_label TEXT,
    equipment_ids TEXT,  -- JSON: ["1", "2", "3"]
    signal_ids TEXT,     -- JSON: ["5", "6", "7"]  
    filter_selections TEXT, -- JSON: {"equipment_1": {"dcu": "1"}}
    position_data TEXT,  -- JSON: {"x": 0, "y": 0, "w": 4, "h": 2}
    styling_config TEXT, -- JSON: {"colors": ["#ff0000"]}
    created_at DATETIME,
    updated_at DATETIME
);

-- Time settings table
CREATE TABLE page_time_settings (
    page_id TEXT PRIMARY KEY,
    default_time_range TEXT,
    default_refresh_rate TEXT,
    last_time_start TEXT,
    last_time_end TEXT,
    last_range_type TEXT,
    created_at DATETIME,
    updated_at DATETIME
);