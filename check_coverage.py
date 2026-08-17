import pandas as pd
from pathlib import Path

files = {
    "profitandloss": "profitandloss.xlsx",
    "balancesheet": "balancesheet.xlsx",
    "cashflow": "cashflow.xlsx",
}

dfs = {}

for name, filename in files.items():
    path = Path("data/raw") / filename
    df = pd.read_excel(path, header=1)

    df["year"] = (
        df["year"]
        .astype(str)
        .str.replace(
            r"^Mar-(\d{2})$",
            lambda m: f"Mar 20{m.group(1)}",
            regex=True
        )
    )

    dfs[name] = df

keys = {}

for name, df in dfs.items():
    keys[name] = set(
        zip(df["company_id"], df["year"])
    )

all_keys = set().union(*keys.values())

print("=" * 70)
print("COMPANY-YEAR COVERAGE CHECK")
print("=" * 70)

for name in keys:
    print(f"{name}: {len(keys[name])} company-year records")

print("\nMissing company-year combinations:")
print("-" * 70)

for name in keys:
    missing = all_keys - keys[name]

    print(f"{name} missing: {len(missing)}")

    if missing:
        print(sorted(missing)[:20])

print("\nCompany counts:")

for name, df in dfs.items():
    print(f"{name}: {df['company_id'].nunique()}")