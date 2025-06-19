
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
