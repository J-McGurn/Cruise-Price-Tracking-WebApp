from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

DB_FILE = os.path.join(os.path.dirname(__file__), "all_cruises.db")
print("Using database at:", DB_FILE)


def get_cruises(table_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")  # fetch all columns
    rows = cursor.fetchall()

    columns = [col[0] for col in cursor.description]

    cruises = []
    for row in rows:
        cruise = {columns[i]: row[i] for i in range(len(columns))}

        # Normalize date_checked
        raw_date = cruise.get("date_checked")
        if raw_date:
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):  # add any formats you expect
                try:
                    dt = datetime.strptime(raw_date, fmt)
                    cruise["date_checked"] = dt.strftime("%d/%m/%Y")
                    break
                except ValueError:
                    continue

        cruises.append(cruise)

    conn.close()
    return cruises


# Endpoint for P&O
@app.route("/cruises/po", methods=["GET"])
def cruises_po():
    return jsonify(get_cruises("po_cruises"))


# Endpoint for Princess
@app.route("/cruises/princess", methods=["GET"])
def cruises_princess():
    return jsonify(get_cruises("princess_cruises"))


if __name__ == "__main__":
    app.run(debug=True)