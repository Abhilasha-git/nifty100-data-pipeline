import sqlite3
from pathlib import Path

import pandas as pd

DB = "db/nifty100.db"

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

conn = sqlite3.connect(DB)

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn,
)

pl = pd.read_sql(
    "SELECT * FROM profitandloss",
    conn,
)

conn.close()

# latest year only
ratios = (
    ratios.sort_values("year")
    .groupby("company_id")
    .tail(1)
)

pl = (
    pl.sort_values("year")
    .groupby("company_id")
    .tail(1)
)

df = ratios.merge(
    pl,
    on=["company_id", "year"],
    how="left",
)

results = []

for _, row in df.iterrows():

    company = row.company_id

    # -------------------------
    # PRO 1
    # -------------------------
    if row.return_on_equity_pct > 20:

        results.append({
            "company_id": company,
            "type": "pro",
            "rule_id": "PRO1",
            "text": "Consistently high return on equity above 20% demonstrates exceptional capital efficiency.",
            "confidence_pct": 90,
        })

    # -------------------------
    # PRO 2
    # -------------------------
    if row.free_cash_flow_cr > 0:

        results.append({
            "company_id": company,
            "type": "pro",
            "rule_id": "PRO2",
            "text": "Strong free cash flow generation signals healthy business fundamentals.",
            "confidence_pct": 85,
        })

    # -------------------------
    # PRO 3
    # -------------------------
    if row.debt_to_equity == 0:

        results.append({
            "company_id": company,
            "type": "pro",
            "rule_id": "PRO3",
            "text": "Debt-free balance sheet provides financial flexibility and eliminates interest burden.",
            "confidence_pct": 95,
        })

    # -------------------------
    # PRO 4
    # -------------------------
    revenue = pd.to_numeric(
        row.revenue_cagr_5yr,
        errors="coerce"
    )

    if pd.notna(revenue) and revenue > 15:

        results.append({
            "company_id": company,
            "type": "pro",
            "rule_id": "PRO4",
            "text": "Revenue growing above 15% CAGR reflects strong business momentum.",
            "confidence_pct": 90,
        })

    # -------------------------
    # PRO 5
    # -------------------------
    if row.operating_profit_margin_pct > 25:

        results.append({
            "company_id": company,
            "type": "pro",
            "rule_id": "PRO5",
            "text": "Operating margin above 25% indicates strong pricing power and cost discipline.",
            "confidence_pct": 88,
        })

    # -------------------------
    # PRO 6
    # -------------------------
    pat = pd.to_numeric(
        row.pat_cagr_5yr,
        errors="coerce"
    )

    if pd.notna(pat) and pat > 20:

        results.append({
            "company_id": company,
            "type": "pro",
            "rule_id": "PRO6",
            "text": "Net profit compounding above 20% creates significant shareholder value.",
            "confidence_pct": 90,
        })
        
    # -------------------------
    # CON 1
    # -------------------------
    if row.debt_to_equity > 2:

        results.append({
            "company_id": company,
            "type": "con",
            "rule_id": "CON1",
            "text": f"Debt-to-equity ratio of {row.debt_to_equity:.2f} is elevated.",
            "confidence_pct": 90,
        })

    # -------------------------
    # CON 2
    # -------------------------
    if row.free_cash_flow_cr < 0:

        results.append({
            "company_id": company,
            "type": "con",
            "rule_id": "CON2",
            "text": "Negative free cash flow raises concern about cash generation quality.",
            "confidence_pct": 85,
        })

    # -------------------------
    # CON 3
    # -------------------------
    if row.operating_profit_margin_pct < 10:

        results.append({
            "company_id": company,
            "type": "con",
            "rule_id": "CON3",
            "text": "Operating margin is weak and should be monitored.",
            "confidence_pct": 75,
        })

    # -------------------------
    # CON 4
    # -------------------------
    if row.net_profit < 0:

        results.append({
            "company_id": company,
            "type": "con",
            "rule_id": "CON4",
            "text": "Company reported a net loss in the latest financial year.",
            "confidence_pct": 95,
        })

    # -------------------------
    # CON 5
    # -------------------------
    if row.interest_coverage < 1.5:

        results.append({
            "company_id": company,
            "type": "con",
            "rule_id": "CON5",
            "text": "Interest coverage ratio below 1.5x indicates financial stress.",
            "confidence_pct": 90,
        })

    # -------------------------
    # CON 6
    # -------------------------
    if pd.notna(revenue) and revenue < 5:

        results.append({
            "company_id": company,
            "type": "con",
            "rule_id": "CON6",
            "text": "Revenue CAGR below 5% suggests weak business momentum.",
            "confidence_pct": 80,
        })
        
pros_cons = pd.DataFrame(results)

pros_cons = pros_cons[
    pros_cons["confidence_pct"] > 60
]

conn = sqlite3.connect(DB)

companies = pd.read_sql(
    "SELECT id FROM companies",
    conn,
)

conn.close()

for company in companies["id"]:

    company_rows = pros_cons[
        pros_cons["company_id"] == company
    ]

    if not (company_rows["type"] == "pro").any():

        pros_cons.loc[len(pros_cons)] = {
            "company_id": company,
            "type": "pro",
            "rule_id": "DEFAULT_PRO",
            "text": "Stable business with established operations.",
            "confidence_pct": 65,
        }

    if not (company_rows["type"] == "con").any():

        pros_cons.loc[len(pros_cons)] = {
            "company_id": company,
            "type": "con",
            "rule_id": "DEFAULT_CON",
            "text": "Business performance should be monitored for future improvements.",
            "confidence_pct": 65,
        }

pros_cons.to_csv(
    OUTPUT / "pros_cons_generated.csv",
    index=False,
)

print("pros_cons_generated.csv created")
print(f"{len(pros_cons)} rows generated")