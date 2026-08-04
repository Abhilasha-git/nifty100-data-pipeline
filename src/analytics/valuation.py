import sqlite3
import pandas as pd

DB = "db/nifty100.db"

conn = sqlite3.connect(DB)

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn,
)

companies = pd.read_sql(
    """
    SELECT
        id AS company_id,
        company_name
    FROM companies
    """,
    conn,
)

conn.close()

market = pd.read_excel(
    "data/raw/supporting_datasets/market_cap.xlsx"
)

sectors = pd.read_excel(
    "data/raw/supporting_datasets/sectors.xlsx"
)

numeric_cols = [
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
]

for col in numeric_cols:
    ratios[col] = pd.to_numeric(
        ratios[col],
        errors="coerce",
    )
    
latest_ratios = (
    ratios
    .sort_values("year")
    .groupby("company_id")
    .tail(1)
)

valuation = (
    latest_ratios
    .merge(companies, on="company_id", how="left")
    .merge(sectors[["company_id", "broad_sector"]], on="company_id", how="left")
    .merge(
        market[
            [
                "company_id",
                "year",
                "market_cap_crore",
                "pe_ratio",
                "pb_ratio",
                "ev_ebitda",
            ]
        ],
        on=["company_id", "year"],
        how="left",
    )
)

valuation["fcf_yield_pct"] = (
    valuation["free_cash_flow_cr"]
    / valuation["market_cap_crore"]
) * 100

sector_pe = (
    valuation
    .groupby("broad_sector")["pe_ratio"]
    .median()
    .reset_index()
)

sector_pe.columns = [
    "broad_sector",
    "sector_median_pe",
]

valuation = valuation.merge(
    sector_pe,
    on="broad_sector",
    how="left",
)

median_pe = (
    market
    .groupby("company_id")["pe_ratio"]
    .median()
    .reset_index()
)

median_pe.columns = [
    "company_id",
    "median_pe_5yr",
]

valuation = valuation.merge(
    median_pe,
    on="company_id",
    how="left",
)

valuation["pe_vs_sector_median_pct"] = (
    (
        valuation["pe_ratio"]
        - valuation["sector_median_pe"]
    )
    / valuation["sector_median_pe"]
) * 100

def valuation_flag(row):

    if pd.isna(row["pe_ratio"]) or pd.isna(row["sector_median_pe"]):
        return "Unknown"

    if row["pe_ratio"] > row["sector_median_pe"] * 1.5:
        return "Caution"

    elif row["pe_ratio"] < row["sector_median_pe"] * 0.7:
        return "Discount"

    else:
        return "Fair"


valuation["flag"] = valuation.apply(
    valuation_flag,
    axis=1,
)

valuation_summary = valuation[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "fcf_yield_pct",
        "median_pe_5yr",
        "pe_vs_sector_median_pct",
        "flag",
    ]
].copy()

valuation_summary.columns = [
    "company_id",
    "company_name",
    "sector",
    "P/E",
    "P/B",
    "EV/EBITDA",
    "FCF_yield_pct",
    "5yr_median_PE",
    "PE_vs_sector_median_pct",
    "flag",
]

import os

os.makedirs("output", exist_ok=True)

valuation_summary.to_excel(
    "output/valuation_summary.xlsx",
    index=False,
)

valuation_flags = valuation_summary[
    valuation_summary["flag"].isin(
        ["Caution", "Discount"]
    )
]

valuation_flags.to_csv(
    "output/valuation_flags.csv",
    index=False,
)

print("Valuation module completed.")

print("Created:")
print("output/valuation_summary.xlsx")
print("output/valuation_flags.csv")