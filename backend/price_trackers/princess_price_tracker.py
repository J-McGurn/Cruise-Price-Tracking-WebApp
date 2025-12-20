import os
import json
import sqlite3
import requests
from datetime import datetime, date
from pathlib import Path

def main():
    # === TEST MODE ===
    TEST_MODE = False  # 👈 Set to False for real run
    print(f"Running in {'TEST' if TEST_MODE else 'LIVE'} mode")
    
    # === CONFIG ===
    config_path = Path(__file__).resolve().parents[1] / "config" / "princess_config.json"
    removed_path = Path(__file__).resolve().parents[1] / "config" / "removed_cruises.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    with open(removed_path, 'r') as f:
        removed = json.load(f)
        
    cruise_codes = config.get("cruise_codes", [])
    cabins = config.get("cabins", {})
    ships = config.get("ships", {})
    ports = config.get("ports", {})

    today = date.today().isoformat()
    USD_TO_GBP = 0.78

    # === HEADERS/COOKIES ===
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en;q=0.5",
        "AppId": '{"agencyId":"DIRPB","cruiseLineCode":"PCL","sessionId":"532ab9fb-d710-4c27-a457-58ac07c8c132","systemId":"PB","gdsCookie":"CO=GB"}',
        "BookingCompany": "PO",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://www.princess.com",
        "pcl-client-id": "32e7224ac6cc41302f673c5f5d27b4ba",
        "ProductCompany": "PC",
        "Referer": "https://www.princess.com",
        "ReqSrc": "W",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
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
    CREATE TABLE IF NOT EXISTS princess_cruises (
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
        obc            REAL,
        total_price    REAL
    )
    """)
    conn.commit()

    # === STEP 1: Get metadata dump once ===
    url_meta = (
        "https://gw.api.princess.com/pcl-web/internal/resdb/p1.0/products"
        "?agencyCountry=GB&cruiseType=C&voyageStatus=A&webDisplay=Y"
        "&promoFilter=all&light=false"
    )
    response_meta = requests.get(url_meta, headers=headers, cookies=cookies)
    cruise_meta_list = []

    if response_meta.status_code == 200:
        cruise_meta_list = response_meta.json().get("products", [])
        print(f"📥 Retrieved {len(cruise_meta_list)} cruises from metadata API")   
    else:
        print(f"❌ Failed to fetch metadata API ({response_meta.status_code})")


    # === STEP 2: Loop through fares API ===
    for cruise_code in cruise_codes:
        url_fares = f"https://gw.api.princess.com/pcl-web/internal/caps/pc/pricing/v1/cruises/{cruise_code}"
        payload = {
            "booking": {
                "bookingAgency": {
                    "id": "DIRPB",
                    "address": {"stateId":"X","countryId":"GB"},
                    "phones":[{"phoneTypeId":"W","number":"1234567"},{"phoneTypeId":"F","number":"11111111"}],
                    "creditCardChargeFeesFlag":"Y",
                    "countryCanBooks":["IE"],
                    "borderCountries":["GB","GI","MT","IE"],
                    "currencies":[{"id":"GBP"},{"id":"EUR"}],
                    "collectDirectInfoFlag":"N",
                    "dsms":[{"year":"2025","region":"R0","district":"00"}],
                    "commissions":[{"year":"2025","associationCode":"@DEFAULT","association":"DEFAULT ASSOCIATION","salesProgram":"DI","typeFlag":"DIR"}],
                    "internationalFaxFlag":"Y",
                    "confirmationMethod":"F",
                    "edocsFlag":"N"
                },
                "currencyCode":"GBP",
                "guests":[{"country":"GB","homeCity":"LON"},{"country":"GB","homeCity":"LON"}],
                "couponCodes":[]
            },
            "filters":{
                "availabilities":["Y","G","B"],
                "cruiseType":"C",
                "cruises": [cruise_code],
                "meta":"I"
            },
            "leadInBy":"itins",
            "retrieveFlags":{
                "additionalGuestFare": True,
                "averageFare": False,
                "fareType": "BESTFARE",
                "includeMisc": False,
                "includeTfpe": True,
                "roundUpFare": True,
                "subMeta": True,
                "zones": True
            }
        }
        
        response_fares = requests.post(url_fares, json=payload, headers=headers, cookies=cookies)
        
        if response_fares.status_code != 200:
            print(f"❌ Error {response_fares.status_code} for cruise {cruise_code}")
            continue

        fares_data = response_fares.json()
        print(f"✅ Got fares for {cruise_code}")
        
        fare_products = fares_data.get("products", [])
        if not fare_products:
            print(f"No products found for cruise code {cruise_code} - removing from tracking")
            remove_cruise(cruise_code, "Unknown", config, removed, "No products found in Metadata")
            continue
        else:
            fare_product = fare_products[0]
            meta_id = fare_product["id"]
            
            # -- Find corresponding metadata --
            meta_product = next(
                (p for p in cruise_meta_list if p.get("id") == meta_id),
                None
            )
            if not meta_product:
                print(f"Product with id {meta_id} not found - removing from tracking")
                remove_cruise(cruise_code, "Unknown", config, removed, "No matching product in Metadata")
                continue
            
            cruise_name = meta_product.get("name")
            meta_cruise = next(
                (c for c in meta_product.get("cruises", []) if c.get("id") == cruise_code),
                None
            )
            if not meta_cruise:
                print(f"Cruise with id {cruise_code} not found under product {meta_id}")
                remove_cruise(cruise_code, cruise_name, config, removed, "No matching cruise in Metadata")
                continue
            ship_id = meta_cruise["voyage"]["ship"]["id"]
            ship_name = ships.get(ship_id, ship_id)
            departure_port_id = meta_cruise["voyage"]["startPortId"]
            departure_port_name = ports.get(departure_port_id, departure_port_id)
            departure_date = meta_cruise["voyage"]["sailDate"]
            departure_date = datetime.strptime(departure_date, "%Y%m%d").strftime("%d/%m/%Y")
            duration = meta_cruise["voyage"]["duration"]
            
            # -- Find cruise data --
            cruise = fare_product.get("cruises", [])[0]
            
            # Flip mapping so we can look up cabin names by ID  
            id_to_name = {v: k for k, v in cabins.items()}
            
            fares = {
                "BESTFARE": {},
                "BESTVALUE": {}
            }
            
            for fare in cruise.get("pricing", {}).get("fares", []):
                faretype = fare.get("fareType")

                for category in fare.get("categories", []):
                    cabin_id = category.get("id")
                    if cabin_id not in id_to_name:
                        continue  # skip other cabin types
                    cabin_name = id_to_name[cabin_id]

                    # find guest 1
                    guest1 = next((g for g in category.get("guests", []) if g.get("id") == 1), None)
                    if not guest1:
                        continue
                    
                    # find guest 2
                    guest2 = next((g for g in category.get("guests", []) if g.get("id") == 2), None)
                    if not guest2:
                        continue
                    
                    price = guest1.get("fare") + guest2.get("fare")
                    obc_usd = guest1.get("obc", 0) + guest2.get("obc", 0)
                    obc = round(obc_usd * USD_TO_GBP, 2) if obc_usd else 0 # convert to GBP
                    
                    
                    # save into fare_results
                    fares[faretype][cabin_name] = {
                        "price": price,
                        "obc": obc,
                        "net_price": price - obc 
                    }
                    
            # === STEP 3: Insert Into DB ===
            for fare_type, fare_cabins in fares.items():
                for cabin_name, data in fare_cabins.items():
                    if not data or not data.get("price"):
                        continue
                     
                    cursor.execute("""
                        INSERT INTO princess_cruises (
                            date_checked, cruise_code, cruise_name, ship_name, departure_port,
                            departure_date, duration, cabin_type, fare_type, cabin_price,
                            obc, total_price
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        today,
                        cruise_code,
                        cruise_name,
                        ship_name,
                        departure_port_name,
                        departure_date,
                        duration,
                        cabin_name,
                        fare_type,
                        data["price"],
                        data["obc"],
                        data["net_price"]
                    ))

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
    
def remove_cruise(cruise_code, cruise_name, config, removed, reason):
    cruise_codes = config.get("cruise_codes", [])
    if cruise_code in cruise_codes:
        cruise_codes.remove(cruise_code)
        removed.append({
            "timestamp": datetime.now().isoformat(),
            "brand": "princess",
            "cruise_code": cruise_code,
            "cruise_name": cruise_name,
            "reason": reason
        })
    
if __name__ == "__main__":
    main()