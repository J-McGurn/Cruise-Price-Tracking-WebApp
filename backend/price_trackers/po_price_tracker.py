import os
import json
import requests
import sqlite3
from datetime import datetime, date
from pathlib import Path

def main():
    # === TEST MODE ===
    TEST_MODE = False  # 👈 Set to False for real run
    print(f"Running in {'TEST' if TEST_MODE else 'LIVE'} mode")
    
    # === CONFIG ===
    config_path = Path(__file__).resolve().parents[1] / "config" / "po_config.json"
    removed_path = Path(__file__).resolve().parents[1] / "config" / "removed_cruises.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    with open(removed_path, 'r') as f:
        removed = json.load(f)
        
    cruise_codes = config.get("cruise_codes", [])
    cabins = config.get("cabins", {})
    routes = config.get("routes", {})
    ships = config.get("ships", {})
    ports = config.get("ports", {})

    today = date.today()

    # === HEADERS/COOKIES ===
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en-GB,en;q=0.5",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0",
        "Referer": "https://www.pocruises.com/",
        "Content-Type": "application/json",
        "brand": "po",
        "country": "GB",
        "currencyCode": "GBP",
        "locale": "en_GB"
    }
    cookies = {
        "countryCode": "GB",
        "currencyCode": "GBP"
    }

    # === DATABASE SETUP ===
    if TEST_MODE:
        conn = sqlite3.connect(":memory:")  # In-memory DB for testing
        print("⚙️ Using in-memory database (no data will persist)")
    else:
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(ROOT_DIR, "all_cruises.db")
        conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS po_cruises (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
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
    )
    """)
    conn.commit()

    # === LOOP THROUGH CRUISES ===
    for cruise_code in cruise_codes[:]:  # copy list to safely modify
        params = {
            "noOfGuests[adults]": 2,
            "noOfGuests[childs]": 0,
            "noOfGuests[infants]": 0,
        }
        url = f"https://www.pocruises.com/api/v2/price/cruise/{cruise_code}"
        print(f"Fetching {cruise_code}...")

        try:
            response = requests.get(
                url,
                headers=headers,
                cookies=cookies,
                params=params,
                timeout=50
            )
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Request error for {cruise_code}: {e}")
            continue

        try:
            data = response.json().get('data', {}) or {}
        except Exception as e:
            print(f"❌ JSON parse error for {cruise_code}: {e}")
            continue
        
        cruise_name = routes.get(cruise_code, cruise_code)
        dep_date_str = data.get('sailingDate')
        try:
            dep_date_obj = datetime.strptime(dep_date_str, "%Y-%m-%d").date()
            dep_date_formatted = dep_date_obj.strftime("%d/%m/%y")
        except Exception:
            dep_date_obj = None
            dep_date_formatted = dep_date_str or "N/A"
        
        # === CHECK IF DEPARTED ===
        if dep_date_obj and dep_date_obj <= today:
            print(f"🛳️ {cruise_code} ({cruise_name}) has already departed — removing from tracking.")
            cruise_codes.remove(cruise_code)
            del config["routes"][cruise_code]
            removed.append({
                "timestamp": datetime.now().isoformat(),
                "brand": "po",
                "cruise_code": cruise_code,
                "cruise_name": cruise_name,
                "reason": "departed"
            })
            continue
            
        duration = data.get('duration', 'N/A')
        ship_code = data.get('shipCode', 'N/A')
        ship_name = ships.get(ship_code, ship_code)
        depart_port = data.get('departPortId', 'N/A')
        depart_port_name = ports.get(depart_port, depart_port)
        room_types = data.get('roomTypes', [])
        
        has_any_available = False

        for room in room_types:
            cabin_type = room.get('name')
            if cabin_type not in cabins:
                continue  # skip non-tracked cabin types

            fares = {
                "Saver": {"price": None, "fixed_obc": 0, "bonus_obc": 0, "net_price": None},
                "Select": {"price": None, "fixed_obc": 0, "bonus_obc": 0, "net_price": None},
            }
            select_package_price = None
            room_has_price = False

            for category in room.get('categories', []):
                if category.get('id') == cabins[cabin_type]:
                    for price_info in category.get('price', []):
                        fare = price_info.get('fare')
                        price_data = price_info.get('price')
                        price_val = price_data.get('parsedValue') if isinstance(price_data, dict) else price_data
                        if not price_val or price_val == 0:
                            continue

                        room_has_price = True  # ✅ at least one available cabin

                        if fare in ["KU2", "FU2"]:
                            fares["Saver"]["price"] = price_val
                        elif fare == "KD1":
                            fares["Select"]["price"] = price_val
                            obc_data = price_info.get('onBoardCredits') or price_info.get('onBoardCredit')
                            if isinstance(obc_data, dict):
                                fares["Select"]["bonus_obc"] = obc_data.get('amount', 0)
                            elif isinstance(obc_data, list) and obc_data:
                                fares["Select"]["bonus_obc"] = obc_data[0].get('amount', 0)

                            # Perks
                            for perk in price_info.get("perks", []):
                                if perk.get("rateCode") == "KD1":
                                    perk_obc = perk.get("onBoardCredit")
                                    if isinstance(perk_obc, dict):
                                        fares["Select"]["fixed_obc"] = perk_obc.get("parsedValue", 0)
                                    elif isinstance(perk_obc, (int, float)):                                        
                                        fares["Select"]["fixed_obc"] = perk_obc
                        elif fare in ["K8W", "K2S", "KT1"]:
                            select_package_price = price_val

            if not room_has_price:
                print(f"❌ {cruise_code} - {cabin_type} sold out (skipping).")
                continue

            has_any_available = True

            # Calculate final prices
            if fares["Select"]["price"] is not None:
                fares["Select"]["net_price"] = (
                    fares["Select"]["price"] - fares["Select"]["bonus_obc"] - fares["Select"]["fixed_obc"]
                )

            drinks_price = None
            if fares["Select"]["price"] and select_package_price:
                drinks_price = select_package_price - fares["Select"]["price"]

            # Insert both fares
            for fare_type, fare_data in fares.items():
                if fare_data["price"] is None:
                    continue
                cursor.execute("""
                INSERT INTO po_cruises (
                    date_checked, cruise_code, cruise_name, ship_name, departure_port,
                    departure_date, duration, cabin_type, fare_type, cabin_price,
                    fixed_obc, bonus_obc, total_price, drinks_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    today.isoformat(),
                    cruise_code,
                    cruise_name,
                    ship_name,
                    depart_port_name,
                    dep_date_formatted,
                    duration,
                    cabin_type,
                    fare_type,
                    fare_data["price"],
                    fare_data["fixed_obc"],
                    fare_data["bonus_obc"],
                    fare_data["net_price"] if fare_type == "Select" else fare_data["price"],
                    drinks_price
                ))

        # === If all sold out ===
        if not has_any_available:
            print(f"🛑 All tracked cabins sold out for {cruise_code} ({cruise_name}) — removing from config.")
            cruise_codes.remove(cruise_code)
            del config["routes"][cruise_code]
            removed.append({
                "timestamp": datetime.now().isoformat(),
                "brand": "po",
                "cruise_code": cruise_code,
                "cruise_name": cruise_name,
                "reason": "sold_out"
            })
            
    # === SAVE UPDATED CONFIG ===
    if not TEST_MODE:
        config["cruise_codes"] = cruise_codes
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

        with open(removed_path, 'w') as f:
            json.dump(removed, f, indent=4)        

    conn.commit()
    conn.close()
    print("\n✅ Done! Config and database updated successfully.")

if __name__ == "__main__":
    main()