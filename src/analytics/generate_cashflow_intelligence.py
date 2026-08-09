import sqlite3
from pathlib import Path

import pandas as pd

DB = "db/nifty100.db"

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

conn = sqlite3.connect(DB)

companies = pd.read_sql(
    "SELECT id AS company_id FROM companies",
    conn,
)

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn,
)

cash = pd.read_sql(
    "SELECT * FROM cashflow",
    conn,
)

bs = pd.read_sql(
    "SELECT * FROM balancesheet",
    conn,
)

pl = pd.read_sql(
    "SELECT company_id, year, sales, net_profit FROM profitandloss",
    conn,
)

conn.close()


# ---------------------------------------------------------
# CFO quality
# ---------------------------------------------------------

ratios["cfo_quality_score"] = (
    ratios.groupby("company_id")["cfo_pat_ratio"]
    .transform("mean")
)

def quality_label(x):
    if pd.isna(x):
        return "N/A"
    if x > 1:
        return "High Quality"
    if x >= 0.5:
        return "Moderate"
    return "Accrual Risk"


ratios["cfo_quality_label"] = (
    ratios["cfo_quality_score"].apply(quality_label)
)


# ---------------------------------------------------------
# Cash-flow intelligence
# ---------------------------------------------------------

cash = cash.merge(
    pl,
    on=["company_id", "year"],
    how="left",
)

cash["capex_intensity_pct"] = (
    cash["investing_activity"].abs()
    / cash["sales"].replace(0, pd.NA)
    * 100
)


def capex_label(x):
    if pd.isna(x):
        return "N/A"
    if x < 3:
        return "Asset Light"
    if x <= 8:
        return "Moderate"
    return "Capital Intensive"


cash["capex_label"] = (
    cash["capex_intensity_pct"].apply(capex_label)
)


cash["distress_flag"] = (
    (cash["operating_activity"] < 0)
    &
    (cash["financing_activity"] > 0)
)


# ---------------------------------------------------------
# Balance-sheet intelligence
# ---------------------------------------------------------

bs = bs.sort_values(
    ["company_id", "year"]
)

bs["borrowings_prev"] = (
    bs.groupby("company_id")["borrowings"]
    .shift(1)
)

bs = bs.merge(
    cash[
        [
            "company_id",
            "year",
            "financing_activity",
        ]
    ],
    on=["company_id", "year"],
    how="left",
)

bs["deleveraging_flag"] = (
    (bs["financing_activity"] < 0)
    &
    (bs["borrowings"] < bs["borrowings_prev"])
)


# ---------------------------------------------------------
# Latest available record per company
# ---------------------------------------------------------

latest_ratios = (
    ratios.sort_values("year")
    .groupby("company_id")
    .tail(1)
)

latest_cash = (
    cash.sort_values("year")
    .groupby("company_id")
    .tail(1)
)

latest_bs = (
    bs.sort_values("year")
    .groupby("company_id")
    .tail(1)
)


# ---------------------------------------------------------
# IMPORTANT:
# Start from ALL companies.
#
# This prevents companies with missing cash-flow or
# balance-sheet data from disappearing.
# ---------------------------------------------------------

final = companies.merge(
    latest_ratios[
        [
            "company_id",
            "cfo_quality_score",
            "cfo_quality_label",
            "fcf_conversion_rate_pct",
            "capital_allocation_pattern",
        ]
    ],
    on="company_id",
    how="left",
)

final = final.merge(
    latest_cash[
        [
            "company_id",
            "capex_intensity_pct",
            "capex_label",
            "distress_flag",
        ]
    ],
    on="company_id",
    how="left",
)

final = final.merge(
    latest_bs[
        [
            "company_id",
            "deleveraging_flag",
        ]
    ],
    on="company_id",
    how="left",
)


# ---------------------------------------------------------
# Fill missing categorical flags
# ---------------------------------------------------------

final["cfo_quality_label"] = (
    final["cfo_quality_label"].fillna("N/A")
)

final["capex_label"] = (
    final["capex_label"].fillna("N/A")
)

final["capital_allocation_pattern"] = (
    final["capital_allocation_pattern"].fillna("N/A")
)

final["distress_flag"] = (
    final["distress_flag"].fillna(False)
)

final["deleveraging_flag"] = (
    final["deleveraging_flag"].fillna(False)
)


# ---------------------------------------------------------
# Final output columns
# ---------------------------------------------------------

final = final[
    [
        "company_id",
        "cfo_quality_score",
        "cfo_quality_label",
        "capex_intensity_pct",
        "capex_label",
        "fcf_conversion_rate_pct",
        "distress_flag",
        "deleveraging_flag",
        "capital_allocation_pattern",
    ]
]

final.rename(
    columns={
        "fcf_conversion_rate_pct": "fcf_conversion_pct",
        "capital_allocation_pattern": "capital_allocation_label",
    },
    inplace=True,
)


# ---------------------------------------------------------
# Write Excel
# ---------------------------------------------------------

final.to_excel(
    OUTPUT / "cashflow_intelligence.xlsx",
    index=False,
)


# ---------------------------------------------------------
# Distress alerts
# ---------------------------------------------------------

alerts = final[
    final["distress_flag"] == True
]

alerts.to_csv(
    OUTPUT / "distress_alerts.csv",
    index=False,
)


# ---------------------------------------------------------
# Verification
# ---------------------------------------------------------

print(
    f"cashflow_intelligence.xlsx created: "
    f"{len(final)} companies"
)

print(
    f"distress_alerts.csv created: "
    f"{len(alerts)} alerts"
)

if len(final) != len(companies):
    raise RuntimeError(
        f"Expected {len(companies)} companies, "
        f"but generated {len(final)}"
    )