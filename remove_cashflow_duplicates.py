import pandas as pd
from pathlib import Path
import shutil

path = Path("data/raw/cashflow.xlsx")
backup = Path("data/raw/cashflow_before_duplicate_removal.xlsx")

# Backup
if not backup.exists():
    shutil.copy2(path, backup)
    print(f"Backup created: {backup}")

# Read file
df = pd.read_excel(path, header=1)

print("Before:", len(df))

# Remove exact duplicate company-year records.
# Keep the first occurrence.
df = df.drop_duplicates(
    subset=["company_id", "year"],
    keep="first"
)

print("After:", len(df))
print("Removed:", 1164 - len(df))

# Preserve two-row Excel structure
with pd.ExcelWriter(path, engine="openpyxl") as writer:

    title = pd.DataFrame(
        [["Bluestock Fintech — Nifty 100  |  Cashflow"]]
    )

    title.to_excel(
        writer,
        index=False,
        header=False,
        startrow=0
    )

    df.to_excel(
        writer,
        index=False,
        startrow=1
    )

print("\nDuplicate removal complete.")

# Verify
duplicates = df.duplicated(
    subset=["company_id", "year"]
).sum()

print("Remaining duplicate company-year rows:", duplicates)