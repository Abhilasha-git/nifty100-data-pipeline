import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"


def run_query(query):
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def main():

    reports = {
        "Top 10 ROE": """
            SELECT
                id,
                company_name,
                roe_percentage
            FROM companies
            ORDER BY roe_percentage DESC
            LIMIT 10;
        """,

        "Top 10 ROCE": """
            SELECT
                id,
                company_name,
                roce_percentage
            FROM companies
            ORDER BY roce_percentage DESC
            LIMIT 10;
        """,

        "Top 10 Book Value": """
            SELECT
                id,
                company_name,
                book_value
            FROM companies
            ORDER BY book_value DESC
            LIMIT 10;
        """,

        "Top 10 Net Profit": """
            SELECT
                company_id,
                year,
                net_profit
            FROM profitandloss
            ORDER BY net_profit DESC
            LIMIT 10;
        """,

        "Dataset Summary": """
            SELECT
                (SELECT COUNT(*) FROM companies) AS companies,
                (SELECT COUNT(*) FROM profitandloss) AS profitandloss,
                (SELECT COUNT(*) FROM balancesheet) AS balancesheet,
                (SELECT COUNT(*) FROM cashflow) AS cashflow,
                (SELECT COUNT(*) FROM analysis) AS analysis,
                (SELECT COUNT(*) FROM documents) AS documents,
                (SELECT COUNT(*) FROM prosandcons) AS prosandcons;
        """
    }

    for title, query in reports.items():
        print("\n" + "=" * 60)
        print(title)
        print("=" * 60)

        df = run_query(query)
        print(df)

    # Save report to CSV
        filename = title.lower().replace(" ", "_") + ".csv"

        df.to_csv(
            f"output/reports/{filename}",
            index=False
        )

        print(f"Saved: output/reports/{filename}")


if __name__ == "__main__":
    main()