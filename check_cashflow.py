import pandas as pd
from pathlib import Path

path = Path("data/raw/cashflow.xlsx")
df = pd.read_excel(path, header=1)

df["calculated_net_cash_flow"] = (
    df["operating_activity"]
    + df["investing_activity"]
    + df["financing_activity"]
)

df["difference"] = (
    df["net_cash_flow"] - df["calculated_net_cash_flow"]
).abs()

print("Cash-flow reconciliation")
print("=========================")
print("Total rows:", len(df))
print("Exact matches:", (df["difference"] == 0).sum())
print("Difference <= 1:", (df["difference"] <= 1).sum())
print("Difference > 1:", (df["difference"] > 1).sum())
print("Maximum difference:", df["difference"].max())

print("\nDifference distribution:")
print(df["difference"].value_counts().sort_index())

print("\nRows with difference > 1:")

print(
    df.loc[
        df["difference"] > 1,
        [
            "id",
            "company_id",
            "year",
            "operating_activity",
            "investing_activity",
            "financing_activity",
            "net_cash_flow",
            "calculated_net_cash_flow",
            "difference",
        ],
    ].to_string(index=False)
)