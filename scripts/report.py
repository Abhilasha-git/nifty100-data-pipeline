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
        """,
        "Top 10 Companies by Latest Net Profit": """
            SELECT
                c.company_name,
                p.year,
                p.net_profit
            FROM companies c
            JOIN profitandloss p
                ON c.id = p.company_id
            WHERE p.year = (
                SELECT MAX(year)
                FROM profitandloss p2
                WHERE p2.company_id = p.company_id
            )
            ORDER BY p.net_profit DESC
            LIMIT 10;
        """,
        
        "Top 10 companies by Latest Sales": """
            SELECT
                c.company_name,
                p.year,
                p.sales
            FROM companies c
            JOIN profitandloss p
                ON c.id = p.company_id
            WHERE p.year = (
                SELECT MAX(year)
                FROM profitandloss p2
                WHERE p2.company_id = p.company_id
            )
            ORDER BY p.sales DESC
            LIMIT 10;
        """,
        "5 Random Companies": """
            SELECT 
                id,
                company_name,
                face_value,
                book_value,
                roce_percentage,
                roe_percentage
            FROM companies
            ORDER BY RANDOM()
            LIMIT 5;
        """,
        "Year Coverage": """
            SELECT
                company_id,
                MIN(year) AS first_year,
                MAX(year) AS last_year,
                COUNT(year) AS total_years
            FROM profitandloss
            GROUP BY company_id
            ORDER BY company_id;
        """,
        "Companies with Less Than 5 Years": """
        SELECT 
            company_id,
            COUNT(year) AS total_years
        FROM profitandloss
        GROUP BY company_id
        HAVING COUNT(year) < 5
        ORDER BY total_years, company_id;
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