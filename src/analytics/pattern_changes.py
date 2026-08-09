import pandas as pd

df = pd.read_csv("output/capital_allocation.csv")

df = df.sort_values(["company_id", "year"])

changes = []

for company, group in df.groupby("company_id"):

    previous = None

    for _, row in group.iterrows():

        current = row["capital_allocation_pattern"]

        if previous is not None and previous != current:

            changes.append({
                "company_id": company,
                "year": row["year"],
                "from_pattern": previous,
                "to_pattern": current,
            })

        previous = current

changes = pd.DataFrame(changes)

changes.to_csv(
    "output/pattern_changes.csv",
    index=False,
)

print(changes.head())
print("pattern_changes.csv created")