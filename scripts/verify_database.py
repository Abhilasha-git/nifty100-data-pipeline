import sqlite3

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 50)
print("Company Count")
print("=" * 50)

cursor.execute("SELECT COUNT(*) FROM companies;")
print(cursor.fetchone()[0])

print("\n" + "=" * 50)
print("Foreign Key Check")
print("=" * 50)

cursor.execute("PRAGMA foreign_key_check;")
rows = cursor.fetchall()

if len(rows) == 0:
    print("PASS - No foreign key violations.")
else:
    print("FAIL - Foreign key violations found:")
    for row in rows:
        print(row)

conn.close()