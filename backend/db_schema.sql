-- Schema for all_cruises.db

-- To create new db (if needed):
    -- Delete old db file
    -- Run command in bash terminal:
        -- sqlite3 all_cruises.db < db_schema.sql

-- P&O Cruises
CREATE TABLE IF NOT EXISTS po_cruises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_checked   TEXT,
    cruise_code    TEXT,
    cruise_name    TEXT,
    ship_name      TEXT,
    departure_port TEXT,
    departure_date TEXT,
    duration       INTEGER,
    cabin_type     TEXT,
    fare_type      TEXT,
    cabin_price    REAL,
    fixed_obc      REAL,
    bonus_obc      REAL,
    total_price    REAL,
    drinks_price   REAL
);

-- Princess Cruises
CREATE TABLE IF NOT EXISTS princess_cruises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_checked   TEXT,
    cruise_code    TEXT,
    cruise_name    TEXT,
    ship_name      TEXT,
    departure_port TEXT,
    departure_date TEXT,
    duration       INTEGER,
    cabin_type     TEXT,
    fare_type      TEXT,
    cabin_price    REAL,
    obc            REAL,
    total_price    REAL
);
