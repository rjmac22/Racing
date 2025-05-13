"""
sync_from_kaggle_db.py

This script synchronizes new rows from a downloaded Kaggle version of `raceform.db` 
into your existing local `raceform.db`. It performs a non-destructive merge — adding only new (race_id, horse) combinations.

🛠 Prerequisites:
- You have downloaded the latest `raceform.db` from Kaggle manually
- You renamed it to: raceform_kaggle.db
- You placed both DBs in: C:/Users/Rob/Documents/Racing/db/

👀 What it does:
1. Connects to both the Kaggle and local databases
2. Compares all (race_id || horse) pairs to find new rows
3. Inserts only those new rows into your local database
"""

import sqlite3
import os

# Paths to both databases
KAGGLE_DB = r"C:\Users\Rob\Documents\Racing\db\raceform_kaggle.db"
LOCAL_DB = r"C:\Users\Rob\Documents\Racing\db\raceform.db"

print("📥 Connecting to both databases...")
src_con = sqlite3.connect(KAGGLE_DB)
dst_con = sqlite3.connect(LOCAL_DB)

# Step 1: Fetch new rows from Kaggle DB not present in local DB
print("🔎 Checking for new race_id + horse combinations...")

# Attach the local DB into the Kaggle DB connection so we can cross-query
src_con.execute(f"ATTACH DATABASE '{LOCAL_DB}' AS local")

# Select all rows from Kaggle that are not in the local DB
query = """
SELECT * FROM main.data
WHERE race_id || '-' || horse NOT IN (
    SELECT race_id || '-' || horse FROM local.data
)
"""

new_rows = src_con.execute(query).fetchall()

if not new_rows:
    print("✅ Local DB already contains all records.")
else:
    print(f"📦 Found {len(new_rows):,} new rows — importing...")

    # Fetch column names from the source DB
    columns = [row[1] for row in src_con.execute("PRAGMA table_info(main.data)")]
    placeholders = ", ".join("?" for _ in columns)
    insert_sql = f"INSERT INTO data ({', '.join(columns)}) VALUES ({placeholders})"

    dst_con.executemany(insert_sql, new_rows)
    dst_con.commit()
    print(f"✅ Imported {len(new_rows):,} new rows into local DB.")

# Clean up
src_con.close()
dst_con.close()
print("🔒 Done. Both connections closed.")
