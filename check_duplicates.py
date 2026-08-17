import pandas as pd
from pathlib import Path

files = [
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
]

for filename in files:
    path = Path("data/raw") / filename
    df = pd.read_excel(path, header=1)

    # Normalize Mar-XX just in case
    df["year"] = (
        df["year"]
        .astype(str)
        .str.replace(
            r"^Mar-(\d{2})$",
            lambda m: f"Mar 20{m.group(1)}",
            regex=True
        )
    )

    duplicates = df[
        df.duplicated(
            subset=["company_id", "year"],
            keep=False
        )
    ].sort_values(["company_id", "year"])

    print("\n" + "=" * 70)
    print(filename)
    print("=" * 70)

    print("Total rows:", len(df))
    print("Duplicate company-year rows:", len(duplicates))

    if len(duplicates) > 0:
        print("\nDuplicates:")
        print(
            duplicates[
                ["id", "company_id", "year"]
            ].to_string(index=False)
        )
    else:
        print("No duplicate company-year records found.")