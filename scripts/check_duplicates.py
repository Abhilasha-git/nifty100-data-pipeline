import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

for table in ["profitandloss", "balancesheet", "cashflow"]:
    print(f"\n===== {table} =====")

    query = f"""
    SELECT
        company_id,
        year,
        COUNT(*) AS cnt
    FROM {table}
    GROUP BY company_id, year
    HAVING COUNT(*) > 1;
    """

    df = pd.read_sql(query, conn)

    if df.empty:
        print("No duplicates found.")
    else:
        print(df)

conn.close()