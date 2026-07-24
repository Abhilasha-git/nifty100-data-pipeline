from pathlib import Path
import sqlite3

import pandas as pd
import yaml

from src.screener.engine import (
    load_financial_ratios,
    apply_filters,
)

DB_PATH = "db/nifty100.db"
CONFIG_PATH = Path("src/config/screener_config.yaml")

def load_config():

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    
def latest_year(df):
    return int(df["year"].max())

def snapshot(df, year):
    return df[df["year"] == year].copy()

def backtest(df, preset_name, filters):

    current = latest_year(df)

    print("=" * 60)
    print(preset_name.upper())
    print("=" * 60)

    for yr in range(current - 5, current + 1):

        snap = snapshot(df, yr)

        result = apply_filters(snap, filters)

        print(
            f"{yr} : {len(result)} companies"
        )
        
def main():

    config = load_config()

    df = load_financial_ratios()

    print("Rows loaded:", len(df))

    for preset, filters in config.items():

        backtest(df, preset, filters)

        print()
        
if __name__ == "__main__":
    main()