import re
from pathlib import Path

import pandas as pd
import sqlite3

DB = "db/nifty100.db"

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

conn = sqlite3.connect(DB)

analysis = pd.read_sql(
    "SELECT * FROM analysis",
    conn,
)

ratios = pd.read_sql(
    """
    SELECT company_id,
           revenue_cagr_5yr,
           pat_cagr_5yr
    FROM financial_ratios
    """,
    conn,
)

conn.close()

pattern = re.compile(
    r"(\d+)\s*Years?:?\s*([\d.]+)%"
)

parsed = []
failures = []

metric_cols = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe",
]

for _, row in analysis.iterrows():

    company = row["company_id"]

    for metric in metric_cols:

        text = str(row[metric])

        match = pattern.search(text)

        if match:

            parsed.append(
                {
                    "company_id": company,
                    "metric_type": metric,
                    "period_years": int(match.group(1)),
                    "value_pct": float(match.group(2)),
                }
            )

        elif "Last Year" in text:

            value = re.findall(r"([\d.]+)%", text)

            if value:

                parsed.append(
                    {
                        "company_id": company,
                        "metric_type": metric,
                        "period_years": 1,
                        "value_pct": float(value[0]),
                    }
                )

        else:

            failures.append(
                {
                    "company_id": company,
                    "metric_type": metric,
                    "text": text,
                }
            )

parsed_df = pd.DataFrame(parsed)
fail_df = pd.DataFrame(failures)

parsed_df.to_csv(
    OUTPUT / "analysis_parsed.csv",
    index=False,
)

fail_df.to_csv(
    OUTPUT / "parse_failures.csv",
    index=False,
)

print("analysis_parsed.csv created")
print("parse_failures.csv created")

# -------------------------------
# CAGR Validation
# -------------------------------

parsed_5yr = parsed_df[
    parsed_df["period_years"] == 5
].copy()

mapping = {
    "compounded_sales_growth": "revenue_cagr_5yr",
    "compounded_profit_growth": "pat_cagr_5yr",
}

validation_rows = []

for _, row in parsed_5yr.iterrows():

    if row["metric_type"] not in mapping:
        continue

    ratio_col = mapping[row["metric_type"]]

    ratio_match = ratios[
        ratios["company_id"] == row["company_id"]
    ]

    if ratio_match.empty:
        continue

    computed = pd.to_numeric(
        ratio_match.iloc[0][ratio_col],
        errors="coerce"
    )

    if pd.isna(computed):
        continue

    difference = abs(row["value_pct"] - computed)

    validation_rows.append(
        {
            "company_id": row["company_id"],
            "metric": row["metric_type"],
            "parsed_value_pct": row["value_pct"],
            "computed_value_pct": computed,
            "difference_pct": round(difference, 2),
            "manual_review": difference > 5,
        }
    )

validation_df = pd.DataFrame(validation_rows)

validation_df.to_csv(
    OUTPUT / "cagr_validation.csv",
    index=False,
)

print("cagr_validation.csv created")