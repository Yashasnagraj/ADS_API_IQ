#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add customer names to the database
Maps customer IDs to their business names
"""

import sys
import sqlite3

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

DB_FILE = "google_ads_data.db"

# Customer ID to Name mapping
CUSTOMER_NAMES = {
    6265362093: "Communn.io",
    5032737756: "Emcee Sons",
    7613138874: "VANAVASI KALYANA"
}

def add_customers_table():
    """Create customers table and populate with known customers."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("[→] Creating customers table...")

    # Create customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            descriptive_name TEXT,
            currency_code TEXT DEFAULT 'INR',
            time_zone TEXT DEFAULT 'Asia/Kolkata',
            status TEXT DEFAULT 'ENABLED',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    print("[✓] Customers table created")
    print("\n[→] Inserting customer names...")

    # Insert customer names
    for customer_id, customer_name in CUSTOMER_NAMES.items():
        cursor.execute("""
            INSERT OR REPLACE INTO customers
            (customer_id, customer_name, descriptive_name, status)
            VALUES (?, ?, ?, 'ENABLED')
        """, (customer_id, customer_name, customer_name))
        print(f"  [✓] Added: {customer_name} (ID: {customer_id})")

    conn.commit()

    # Verify
    print("\n[→] Verifying customers in database...")
    cursor.execute("SELECT customer_id, customer_name FROM customers ORDER BY customer_id")
    customers = cursor.fetchall()

    print("\n📊 Customers in database:")
    for customer_id, customer_name in customers:
        print(f"  • {customer_name} (ID: {customer_id})")

    conn.close()
    print("\n[✓] Customer names added successfully!")

if __name__ == "__main__":
    add_customers_table()
