import sqlite3
import pandas as pd
from pathlib import Path

DB = "db/nifty100.db"

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

conn = sqlite3.connect(DB)

df = pd.read_sql("""
SELECT
    company_id,
    year,
    capital_allocation_pattern
FROM financial_ratios
ORDER BY company_id, year
""", conn)

conn.close()

df.to_csv(
    OUTPUT / "capital_allocation.csv",
    index=False
)

print("capital_allocation.csv created")
print(df.head())
print(f"Rows: {len(df)}")