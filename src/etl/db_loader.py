import sqlite3
from pathlib import Path

from src.etl.loader import load_core_files

DB_PATH = Path("db/nifty100.db")
SCHEMA_PATH = Path("db/schema.sql")


def create_database():
    """
    Create SQLite database and execute schema.sql.
    """

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.commit()
    conn.close()

    print("Database created successfully.")

def load_data():
    """
    Load all datasets into SQLite.
    """

    datasets = load_core_files()

    companies = datasets["companies"]
    valid_ids = set(companies["id"])

    conn = sqlite3.connect(DB_PATH)

    for table_name, df in datasets.items():

        print(f"Loading {table_name}...")

        if table_name != "companies" and "company_id" in df.columns:
            before = len(df)
            df = df[df["company_id"].isin(valid_ids)]
            removed = before - len(df)

            if removed:
                print(f"Removed {removed} invalid rows from {table_name}")

        df.to_sql(
            table_name,
            conn,
            if_exists="append",
            index=False
        )

    conn.commit()
    conn.close()

    print("All tables loaded successfully.")


def main():
    create_database()
    load_data()


if __name__ == "__main__":
    main()