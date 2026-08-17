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


# Only compare the main annual March periods.
annual_periods = {
    f"Mar {year}"
    for year in range(2013, 2025)
}

print("=" * 70)
print("ANNUAL MARCH COVERAGE CHECK")
print("=" * 70)

for name, df in dfs.items():
    annual = df[df["year"].isin(annual_periods)]

    print(f"\n{name}")
    print("-" * 70)

    print("Rows:", len(annual))
    print("Companies:", annual["company_id"].nunique())

    counts = annual.groupby("year")["company_id"].nunique()

    print("\nCompanies per March year:")
    print(counts.to_string())


print("\n" + "=" * 70)
print("MISSING ANNUAL MARCH RECORDS")
print("=" * 70)

# Build company set from all three files
all_companies = set()

for df in dfs.values():
    all_companies.update(df["company_id"].dropna().unique())


for year in sorted(annual_periods):

    print(f"\n--- {year} ---")

    for name, df in dfs.items():

        companies_present = set(
            df.loc[df["year"] == year, "company_id"]
        )

        missing = sorted(all_companies - companies_present)

        print(
            f"{name}: missing {len(missing)}"
        )

        if missing:
            print("  ", missing)