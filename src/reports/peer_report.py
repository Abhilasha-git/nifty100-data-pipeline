import sqlite3
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

DB_PATH = "db/nifty100.db"
OUTPUT = "output/peer_comparison.xlsx"

def load_peer_table():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM peer_percentiles
        WHERE year = 2024
        """,
        conn,
    )

    conn.close()

    return df

def load_company_names():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            id AS company_id,
            company_name
        FROM companies
        """,
        conn,
    )

    conn.close()

    return df

def export_peer_report():

    peer = load_peer_table()
    names = load_company_names()

    peer = peer.merge(
        names,
        on="company_id",
        how="left",
    )

    with pd.ExcelWriter(
        OUTPUT,
        engine="openpyxl",
    ) as writer:

        for group, data in peer.groupby("peer_group_name"):

            values = data.pivot(
            index=["company_id", "company_name"],
            columns="metric",
            values="value",
        )

        percentiles = data.pivot(
            index=["company_id", "company_name"],
            columns="metric",
            values="percentile_rank",
        )

    # Rename percentile columns
        percentiles.columns = [
            f"{c}_percentile" for c in percentiles.columns
        ]

    # Merge values + percentiles
        final = values.join(percentiles)

        final.reset_index(inplace=True)

        final.to_excel(
            writer,
            sheet_name=group[:31],
            index=False,
        )

    print("Saved:", OUTPUT)

    wb = load_workbook(OUTPUT)
    
    GREEN = PatternFill(
        fill_type="solid",
        start_color="C6EFCE",
    )

    YELLOW = PatternFill(
        fill_type="solid",
        start_color="FFEB9C",
    )

    RED = PatternFill(
        fill_type="solid",
        start_color="FFC7CE",
    )
    
    GOLD = PatternFill(
        fill_type="solid",
        start_color="FFD966",
    )

    for ws in wb.worksheets:

        headers = [cell.value for cell in ws[1]]
        

        for col_idx, header in enumerate(headers, start=1):

            if header and str(header).endswith("_percentile"):

                for row in range(2, ws.max_row + 1):

                    cell = ws.cell(row=row, column=col_idx)

                    if cell.value is None:
                        continue

                    if cell.value >= 75:
                        cell.fill = GREEN

                    elif cell.value <= 25:
                        cell.fill = RED

                    else:
                        cell.fill = YELLOW

        print(f"\nSheet: {ws.title}")
        print(headers)

    wb.save(OUTPUT)
    