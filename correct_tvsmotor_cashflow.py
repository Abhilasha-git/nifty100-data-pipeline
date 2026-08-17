from pathlib import Path
from openpyxl import load_workbook

FILE = Path("data/raw/cashflow.xlsx")

print("=" * 80)
print("CORRECTING TVSMOTOR — MAR 2022 CASH FLOW")
print("=" * 80)

wb = load_workbook(FILE)
ws = wb.active

# Find the header row.
header_row = None
headers = {}

for row in ws.iter_rows():
    values = [cell.value for cell in row]

    if "company_id" in values and "year" in values:
        header_row = row[0].row

        for cell in row:
            if cell.value is not None:
                headers[cell.value] = cell.column

        break

if header_row is None:
    raise RuntimeError("Could not find the header row.")

required_columns = [
    "company_id",
    "year",
    "operating_activity",
    "investing_activity",
    "financing_activity",
    "net_cash_flow",
]

for column in required_columns:
    if column not in headers:
        raise RuntimeError(f"Missing required column: {column}")

company_col = headers["company_id"]
year_col = headers["year"]
operating_col = headers["operating_activity"]
investing_col = headers["investing_activity"]
financing_col = headers["financing_activity"]
net_cash_col = headers["net_cash_flow"]

# Find TVSMOTOR Mar 2022.
target_row = None

for row_num in range(header_row + 1, ws.max_row + 1):
    company = ws.cell(row_num, company_col).value
    year = ws.cell(row_num, year_col).value

    if company == "TVSMOTOR" and year == "Mar 2022":
        if target_row is not None:
            raise RuntimeError("Multiple TVSMOTOR Mar 2022 rows found.")

        target_row = row_num

if target_row is None:
    raise RuntimeError("TVSMOTOR Mar 2022 row not found.")

operating = ws.cell(target_row, operating_col).value
investing = ws.cell(target_row, investing_col).value
financing = ws.cell(target_row, financing_col).value
old_value = ws.cell(target_row, net_cash_col).value

calculated = operating + investing + financing

print(f"Old net_cash_flow: {old_value}")
print(f"Calculated value:  {calculated}")

if old_value == calculated:
    print("No correction needed.")
    raise SystemExit(0)

# Make a backup before changing anything.
backup = FILE.with_name("cashflow_before_tvsmotor_correction_v2.xlsx")

if not backup.exists():
    import shutil
    shutil.copy2(FILE, backup)

# Change ONLY the net_cash_flow cell.
ws.cell(target_row, net_cash_col).value = calculated

wb.save(FILE)

print()
print(f"Corrected net_cash_flow: {calculated}")
print(f"Backup: {backup}")
print(f"Corrected file: {FILE}")
print()
print("Correction completed successfully.")