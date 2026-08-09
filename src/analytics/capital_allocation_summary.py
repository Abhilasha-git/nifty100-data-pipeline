import pandas as pd

df = pd.read_csv("output/capital_allocation.csv")

latest_year = df["year"].max()

latest = df[df["year"] == latest_year]

summary = (
    latest.groupby("capital_allocation_pattern")
    .size()
    .reset_index(name="company_count")
    .sort_values("company_count", ascending=False)
)

summary.to_csv(
    "output/capital_allocation_distribution.csv",
    index=False,
)

print(summary)
print("capital_allocation_distribution.csv created")