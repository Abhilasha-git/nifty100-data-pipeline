from pathlib import Path
import pandas as pd
import re

from src.etl.loader import load_core_files


class DataValidator:

    def __init__(self):
        self.datasets = load_core_files()
        self.failures = []

    def add_failure(self, rule, table, severity, message, row=None):
        self.failures.append({
            "rule": rule,
            "table": table,
            "severity": severity,
            "message": message,
            "row": row
        })

    def dq01_primary_key(self):
        companies = self.datasets["companies"]

        duplicates = companies[
            companies["id"].duplicated(keep=False)
        ]

        for _, row in duplicates.iterrows():
            self.add_failure(
                "DQ-01",
                "companies",
                "CRITICAL",
                "Duplicate company id",
                row["id"]
            )
            
    def dq02_company_year(self):

        pnl = self.datasets["profitandloss"]

        duplicates = pnl[
            pnl.duplicated(
                subset=["company_id", "year"],
                keep=False
            )
        ]

        for _, row in duplicates.iterrows():
            self.add_failure(
                "DQ-02",
                "profitandloss",
                "CRITICAL",
                "Duplicate company-year record",
                f"{row['company_id']} ({row['year']})"
            )
            
    def dq03_foreign_keys(self):
        companies = set(self.datasets["companies"]["id"])

        tables = [
            "profitandloss",
            "balancesheet",
            "cashflow",
            "analysis",
            "documents",
            "prosandcons"
        ]

        for table in tables:
            df = self.datasets[table]

            invalid_rows = df[~df["company_id"].isin(companies)]

            for _, row in invalid_rows.iterrows():
                self.add_failure(
                    "DQ-03",
                    table,
                    "CRITICAL",
                    "Invalid company_id",
                    row["company_id"]
                )
                
    def dq04_balance_sheet(self):

        bs = self.datasets["balancesheet"]

        for _, row in bs.iterrows():

            assets = row["total_assets"]
            liabilities = row["total_liabilities"]

        # Skip rows with missing or zero values
            if pd.isna(assets) or pd.isna(liabilities) or assets == 0:
                continue

            difference = abs(assets - liabilities)
            percentage = difference / assets

            if percentage > 0.01:
                self.add_failure(
                    "DQ-04",
                    "balancesheet",
                    "WARNING",
                    f"Balance sheet mismatch ({percentage:.2%})",
                    f"{row['company_id']} ({row['year']})"
                )
                
    def dq05_operating_margin(self):
  
        pnl = self.datasets["profitandloss"]

        for _, row in pnl.iterrows():

            sales = row["sales"]
            operating_profit = row["operating_profit"]
            reported_opm = row["opm_percentage"]

        # Skip missing or invalid values
            if (
                pd.isna(sales)
                or pd.isna(operating_profit)
                or pd.isna(reported_opm)
                or sales == 0
            ):
                continue

            calculated_opm = (operating_profit / sales) * 100

            if abs(calculated_opm - reported_opm) > 1:
                self.add_failure(
                    "DQ-05",
                    "profitandloss",
                    "WARNING",
                    f"OPM mismatch: Expected {calculated_opm:.2f}%, Found {reported_opm:.2f}%",
                    f"{row['company_id']} ({row['year']})"
                )
    
    def dq06_positive_sales(self):

        pnl = self.datasets["profitandloss"]

        invalid = pnl[
            (pnl["sales"].notna()) &
            (pnl["sales"] <= 0)
        ]

        for _, row in invalid.iterrows():
            self.add_failure(
                "DQ-06",
                "profitandloss",
                "WARNING",
                "Sales must be greater than zero",
                f"{row['company_id']} ({row['year']})"
            )
            
    def dq07_net_cash_flow(self):

        cf = self.datasets["cashflow"]

        for _, row in cf.iterrows():

            operating = row["operating_activity"]
            investing = row["investing_activity"]
            financing = row["financing_activity"]
            reported = row["net_cash_flow"]

            if (
                pd.isna(operating)
                or pd.isna(investing)
                or pd.isna(financing)
                or pd.isna(reported)
            ):
                continue

            calculated = operating + investing + financing

            if abs(calculated - reported) > 1:
                self.add_failure(
                    "DQ-07",
                    "cashflow",
                    "WARNING",
                    f"Net cash flow mismatch. Expected {calculated}, Found {reported}",
                    f"{row['company_id']} ({row['year']})"
                )
                
    def dq08_tax_rate(self):
    
        pnl = self.datasets["profitandloss"]

        invalid = pnl[
            (pnl["tax_percentage"].notna()) &
            (
                (pnl["tax_percentage"] < 0) |
                (pnl["tax_percentage"] > 100)
            )
        ]

        for _, row in invalid.iterrows():
            self.add_failure(
                "DQ-08",
                "profitandloss",
                "WARNING",
                "Invalid tax percentage",
                f"{row['company_id']} ({row['year']})"
            )
            
    def dq09_dividend_payout(self):

        pnl = self.datasets["profitandloss"]

        invalid = pnl[
            (pnl["dividend_payout"].notna()) &
            (
                (pnl["dividend_payout"] < 0) |
                (pnl["dividend_payout"] > 100)
            )
        ]

        for _, row in invalid.iterrows():
            self.add_failure(
                "DQ-09",
                "profitandloss",
                "WARNING",
                "Invalid dividend payout percentage",
                f"{row['company_id']} ({row['year']})"
            )
           
    def dq10_url_validation(self):

        url_pattern = re.compile(r"^https?://")

        tables = {
            "companies": [
                "website",
                "nse_profile",
                "bse_profile",
                "chart_link"
            ],
            "documents": [
                "annual_report"
            ]
        }

        for table, columns in tables.items():

            df = self.datasets[table]

            for column in columns:

                if column not in df.columns:
                    continue

                invalid = df[
                    df[column].notna() &
                    ~df[column].astype(str).str.match(url_pattern)
                ]

                for _, row in invalid.iterrows():

                    identifier = row.get("company_id", row.get("id"))

                    self.add_failure(
                        "DQ-10",
                        table,
                        "WARNING",
                        f"Invalid URL in '{column}'",
                        identifier
                    )
                    
    def dq11_eps_sign(self):

        pnl = self.datasets["profitandloss"]

        for _, row in pnl.iterrows():

            net_profit = row["net_profit"]
            eps = row["eps"]

            if pd.isna(net_profit) or pd.isna(eps):
                continue

            if (net_profit < 0 and eps > 0) or (net_profit > 0 and eps < 0):
                self.add_failure(
                    "DQ-11",
                    "profitandloss",
                    "WARNING",
                    "EPS sign inconsistent with Net Profit",
                    f"{row['company_id']} ({row['year']})"
                )  
                
    def dq12_year_coverage(self):

        tables = [
            "profitandloss",
            "balancesheet",
            "cashflow",
            "documents"
        ]

        for table in tables:

            df = self.datasets[table]

            invalid = df[
                df["year"].isna() |
                (df["year"] < 2000) |
                (df["year"] > 2100)
            ]

            for _, row in invalid.iterrows():
                self.add_failure(
                    "DQ-12",
                    table,
                    "WARNING",
                    "Invalid financial year",
                    f"{row['company_id']} ({row['year']})"
                )
                
    def dq13_duplicate_documents(self):

        docs = self.datasets["documents"]

        duplicates = docs[
            docs.duplicated(
                subset=["company_id", "year", "annual_report"],
                keep=False
            )
        ]

        for _, row in duplicates.iterrows():
            self.add_failure(
                "DQ-13",
                "documents",
                "WARNING",
                "Duplicate annual report",
                f"{row['company_id']} ({row['year']})"
            ) 
            
    def dq14_mandatory_fields(self):

        companies = self.datasets["companies"]

        mandatory = [
            "id",
            "company_name",
            "website"
        ]

        for column in mandatory:

            invalid = companies[
                companies[column].isna()
            ]

            for _, row in invalid.iterrows():
                self.add_failure(
                    "DQ-14",
                    "companies",
                    "CRITICAL",
                    f"Missing {column}",
                    row["id"]
                )    
                
    def dq15_numeric_ranges(self):

        companies = self.datasets["companies"]

        checks = [
            "roe_percentage",
            "roce_percentage"
        ]

        for column in checks:

            invalid = companies[
                companies[column].notna() &
                (
                    (companies[column] < -100) |
                    (companies[column] > 100)
                )
            ]

            for _, row in invalid.iterrows():
                self.add_failure(
                    "DQ-15",
                    "companies",
                    "WARNING",
                    f"Invalid {column}",
                    row["id"]
                )  
                
    def dq16_dataset_completeness(self):

        required = [
            "companies",
            "profitandloss",
            "balancesheet",
            "cashflow",
            "analysis",
            "documents",
            "prosandcons"
        ]

        for table in required:

            if self.datasets[table].empty:

                self.add_failure(
                    "DQ-16",
                    table,
                    "CRITICAL",
                    "Dataset is empty"
                )   
    
    def save_report(self):
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        report = pd.DataFrame(self.failures)
        report.to_csv(
            output_dir / "validation_failures.csv",
            index=False
        )

        print("Validation report saved.")

    def validate(self):
        self.dq01_primary_key()
        self.dq02_company_year()
        self.dq03_foreign_keys()
        self.dq04_balance_sheet()
        self.dq05_operating_margin()
        self.dq06_positive_sales()
        self.dq07_net_cash_flow()
        self.dq08_tax_rate()
        self.dq09_dividend_payout()
        self.dq10_url_validation()
        self.dq11_eps_sign()
        self.dq12_year_coverage()
        self.dq13_duplicate_documents()
        self.dq14_mandatory_fields()
        self.dq15_numeric_ranges()
        self.dq16_dataset_completeness()
        self.save_report()


if __name__ == "__main__":
    print("Validator started...")
    validator = DataValidator()
    validator.validate()