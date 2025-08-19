import requests
import sqlite3
from datetime import datetime, date

# === CONFIG ===
cruise_codes = [
    "A542B", "A644A", "A644B", "G614", "B615",
    "K614", "N614", "A625", "A626", "K619"
]

cabin_ids = {
    "Inside": "I_I",
    "Outside": "O_O",
    "Balcony": "B_B"
}

dictionary = {
    "N614": "Spain and Portugal",
    "A542B": "Canary Islands And Madeira Fly-Cruise",
    "A644A": "Canary Islands And Madeira Fly-Cruise",
    "A644B": "Canary Islands And Madeira Fly-Cruise",
    "G614": "Norwegian Fjords",
    "B615": "Norwegian Fjords",
    "K614": "Mediterranean - Spain And France",
    "A625": "Western Mediterranean Fly-Cruise",
    "A626": "Eastern Mediterranean Fly-Cruise",
    "K619": "Mediterranean - Spain And France",
    "VE": "Ventura",
    "AZ": "Azura",
    "IA": "Iona",
    "BR": "Britannia",
    "AR": "Arvia",
    "SOU": "Southampton",
    "TCI": "Tenerife",
    "MLA": "Malta"
}

today = date.today().isoformat()

# === HEADERS/COOKIES ===
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://www.pocruises.com/",
    "brand": "po",
    "locale": "en_GB",
    "country": "GB",
    "currencyCode": "GBP",
    "Content-Type": "application/json",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=0",
    "TE": "trailers",
    "x-dtpc": "2$500274100_5h10vEFMASNKKVCIALBDVRNTKHNIUUUADGGHI-0e0"}

cookies = {
    "countryCode": "GB",
    "currencyCode": "GBP",
}

# === DATABASE SETUP ===
conn = sqlite3.connect("cruises.db")
cursor = conn.cursor()
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

# === LOOP THROUGH CRUISES ===
for cruise_code in cruise_codes:
    url = f"https://www.pocruises.com/api/v2/price/cruise/{cruise_code}?noOfGuests/adults=2&noOfGuests/childs=0&noOfGuests/infants=0"
    print(f"Fetching {cruise_code}...")

    response = requests.get(url, headers=headers, cookies=cookies)

    if response.status_code != 200:
        print(f"❌ Request failed for {cruise_code}: {response.status_code}")
        continue

        # === PARSE RESPONSE ===
    data = response.json().get('data', {})
    cruise_name = dictionary.get(cruise_code, cruise_code)
    departure_date = data.get('sailingDate', 'N/A')
    try:
        departure_date = datetime.strptime(departure_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        departure_date = departure_date  # fallback if API changes format
    duration = data.get('duration', 'N/A')
    ship_code = data.get('shipCode', 'N/A')
    ship_name = dictionary.get(ship_code, ship_code)
    depart_port = data.get('departPortId', 'N/A')
    depart_port_name = dictionary.get(depart_port, depart_port)
    room_types = data.get('roomTypes', [])


    for room in room_types:
        cabin_type = room.get('name')
        if cabin_type not in cabin_ids:
            continue  # skip other cabin types

        fares = {
            "Saver": {"price": None, "fixed_obc": 0, "bonus_obc": 0, "net_price": None},
            "Select": {"price": None, "fixed_obc": 0, "bonus_obc": 0, "net_price": None},
        }
        select_package_price = None

        for category in room.get('categories', []):
            if category.get('id') == cabin_ids[cabin_type]:
                for price_info in category.get('price', []):
                    fare = price_info.get('fare')
                    price_data = price_info.get('price')
                    price_val = price_data.get('parsedValue') if isinstance(price_data, dict) else price_data

                    if fare == "KU2" or fare == "FU2":
                        fares["Saver"]["price"] = price_val
                    elif fare == "KD1":
                        fares["Select"]["price"] = price_val

                        obc_data = price_info.get('onBoardCredits') or price_info.get('onBoardCredit')
                        if isinstance(obc_data, dict):
                            fares["Select"]["bonus_obc"] = obc_data.get('amount', 0)
                        elif isinstance(obc_data, list) and obc_data:
                            fares["Select"]["bonus_obc"] = obc_data[0].get('amount', 0)

                        # Perks
                        perks_data = price_info.get("perks", [])
                        for perk in perks_data:
                            if perk.get("rateCode") == "KD1":
                                perk_obc = perk.get("onBoardCredit")
                                if isinstance(perk_obc, dict):
                                    fares["Select"]["fixed_obc"] = perk_obc.get("parsedValue", 0)
                                elif isinstance(perk_obc, (int, float)):                                        fares["Select"]["fixed_obc"] = perk_obc
                    elif fare == "K8W":
                        select_package_price = price_val

        # Net price and drinks
        if fares["Select"]["price"] is not None:
            fares["Select"]["net_price"] = (
                fares["Select"]["price"] - fares["Select"]["bonus_obc"] - fares["Select"]["fixed_obc"]
            )

        drinks_price = None
        if fares["Select"]["price"] is not None and select_package_price is not None:
            drinks_price = select_package_price - fares["Select"]["price"]

        # Insert both fares into DB
        for fare_type, fare_data in fares.items():
            if fare_data["price"] is None:
                continue
            cursor.execute("""
            INSERT INTO cruises (
                date_checked, cruise_code, cruise_name, ship_name, departure_port,
                departure_date, duration, cabin_type, fare_type, cabin_price,
                fixed_obc, bonus_obc, total_price, drinks_price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                today,
                cruise_code,
                cruise_name,
                ship_name,
                depart_port_name,
                departure_date,
                duration,
                cabin_type,
                fare_type,
                fare_data["price"],
                fare_data["fixed_obc"],
                fare_data["bonus_obc"],
                fare_data["net_price"] if fare_type == "Select" else fare_data["price"],
                drinks_price
            ))
conn.commit()
conn.close()