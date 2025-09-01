import sqlite3

# Create a new database
conn = sqlite3.connect("cruises.db")  # <- new DB file
cursor = conn.cursor()

# Create the table
cursor.execute("""
CREATE TABLE IF NOT EXISTS cruises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_checked TEXT,
    cruise_code TEXT,
    cruise_name TEXT,
    ship_name TEXT,
    departure_port TEXT,
    departure_date TEXT,
    duration INTEGER,
    cabin_type TEXT,
    fare_type TEXT,
    cabin_price REAL,
    fixed_obc REAL,
    bonus_obc REAL,
    total_price REAL,
    drinks_price REAL
)
""")

conn.commit()
conn.close()

print("New empty database and table created successfully!")
