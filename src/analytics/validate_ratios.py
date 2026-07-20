import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

ratios = pd.read_sql("""
SELECT *
FROM financial_ratios
""", conn)

companies = pd.read_sql("""
SELECT
    id,
    company_name,
    roe_percentage,
    roce_percentage
FROM companies
""", conn)

conn.close()

# Keep only the latest year for each company
latest = (
    ratios
    .dropna(subset=["year"])
    .sort_values("year")
    .groupby("company_id")
    .tail(1)
)

comparison = latest.merge(
    companies,
    left_on="company_id",
    right_on="id",
    how="left"
)

comparison["roe_difference"] = (
    comparison["return_on_equity_pct"]
    - comparison["roe_percentage"]
).abs()

comparison["roce_difference"] = (
    comparison["return_on_capital_employed_pct"]
    - comparison["roce_percentage"]
).abs()

anomalies = comparison[
    (comparison["roe_difference"] > 5) |
    (comparison["roce_difference"] > 5)
].copy()

anomalies["category"] = "Needs Review"

anomalies.to_csv(
    "output/ratio_edge_cases.csv",
    index=False
)

with open("output/ratio_edge_cases.log", "w", encoding="utf-8") as f:
    for _, row in anomalies.iterrows():
        f.write(
            f"{row['company_id']} | "
            f"ROE Diff={row['roe_difference']:.2f} | "
            f"ROCE Diff={row['roce_difference']:.2f} | "
            f"{row['category']}\n"
        )

print(f"Logged {len(anomalies)} anomalies.")

print(comparison[
    [
        "company_id",
        "year",
        "return_on_equity_pct",
        "roe_percentage",
        "roe_difference",
        "return_on_capital_employed_pct",
        "roce_percentage",
        "roce_difference"
    ]
].head())