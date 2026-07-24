from pathlib import Path
import sqlite3

import pandas as pd
import yaml

from src.scoring.score_engine import calculate_composite_score
from src.screener.export_excel import export_screener_results
from src.analytics.peer_summary import add_peer_summary
from src.reports.radar import generate_radar_charts
from src.reports.peer_report import export_peer_report

export_peer_report()

DB_PATH = "db/nifty100.db"
CONFIG_PATH = Path("src/config/screener_config.yaml")


def load_config():
    """
    Load screener configuration from YAML.
    """

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_financial_ratios():
    """
    Load latest financial ratios with supporting company data.
    """

    conn = sqlite3.connect(DB_PATH)
    
    sector_df = pd.read_excel(
        "data/raw/supporting_datasets/sectors.xlsx"
    )

    query = """
    SELECT
        fr.*,
        pnl.sales,
        pnl.net_profit,
        pnl.dividend_payout,
        pnl.opm_percentage,
        c.company_name,
        c.book_value,
        c.roce_percentage

    FROM financial_ratios fr

    LEFT JOIN profitandloss pnl
        ON fr.company_id = pnl.company_id
       AND fr.year = pnl.year

    LEFT JOIN companies c
        ON fr.company_id = c.id

    WHERE fr.year = (
        SELECT MAX(fr2.year)
        FROM financial_ratios fr2
        WHERE fr2.company_id = fr.company_id
    )
    """
    

    df = pd.read_sql(query, conn)
    
    sector_df = pd.read_excel(
        "data/raw/supporting_datasets/sectors.xlsx"
    )[
        [
            "company_id",
            "broad_sector",
            "sub_sector",
            "market_cap_category",
        ]
    ]
    
    print("Sector columns:")
    print(sector_df.columns.tolist())

    df = df.merge(
        sector_df,
        on="company_id",
        how="left"
    )
    
    print("Merged columns:")
    print(df.columns.tolist())
    print("Rows loaded:", len(df))

    conn.close()

    return df

def apply_filters(df, filters):
    """
    Apply screener filters to a DataFrame.
    """

    result = df.copy()

    # Convert numeric columns from SQLite
    numeric_cols = [
        "return_on_equity_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "interest_coverage",
        "asset_turnover",
        "sales",
        "net_profit",
        "opm_percentage",
        "roce_percentage",
        "dividend_payout",
    ]

    for col in numeric_cols:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")

    if "roe_min" in filters:
        result = result[
            result["return_on_equity_pct"] >= filters["roe_min"]
        ]

    if "debt_to_equity_max" in filters:
        result = result[
            result["debt_to_equity"] <= filters["debt_to_equity_max"]
        ]

    if "free_cash_flow_min" in filters:
        result = result[
            result["free_cash_flow_cr"] >= filters["free_cash_flow_min"]
        ]

    if "revenue_cagr_5yr_min" in filters:
        result = result[
            result["revenue_cagr_5yr"] >= filters["revenue_cagr_5yr_min"]
        ]

    if "pat_cagr_5yr_min" in filters:
        result = result[
            result["pat_cagr_5yr"] >= filters["pat_cagr_5yr_min"]
        ]
    
    
        # Operating Profit Margin
    if "opm_min" in filters:
        result = result[
            result["opm_percentage"] >= filters["opm_min"]
        ]

    # EPS CAGR
    if "eps_cagr_5yr_min" in filters:
        result = result[
            result["eps_cagr_5yr"] >= filters["eps_cagr_5yr_min"]
        ]

    # Interest Coverage
    if "interest_coverage_min" in filters:
        result = result[
            result["interest_coverage"] >= filters["interest_coverage_min"]
        ]

    # Asset Turnover
    if "asset_turnover_min" in filters:
        result = result[
            result["asset_turnover"] >= filters["asset_turnover_min"]
        ]

    # Sales
    if "sales_min" in filters:
        result = result[
            result["sales"] >= filters["sales_min"]
        ]

    # Net Profit
    if "net_profit_min" in filters:
        result = result[
            result["net_profit"] >= filters["net_profit_min"]
        ]
        
    return result


def main():

    config = load_config()

    df = load_financial_ratios()
    
    df = calculate_composite_score(df)
    df = add_peer_summary(df)
    
    peer = pd.read_excel(
        "data/raw/supporting_datasets/peer_groups.xlsx"
    )[["company_id", "peer_group_name"]]

    df = df.merge(peer, on="company_id", how="left")
    
    print("Generating radar charts...")
    generate_radar_charts(df)
    print("Radar charts finished.")
    
    print(df.columns.tolist())
    
    
    results = {}

    for preset_name, preset in config.items():

        filtered = apply_filters(df, preset)

        filtered = filtered.sort_values(
            by=[
                "peer_percentile_score",
                "composite_quality_score",
                "sector_quality_score",
            ],
            ascending=[False, False, False],
        )
        
        results[preset_name] = filtered

        print("\n", "=" * 60)
        print(preset_name.upper())
        print("=" * 60)

        print(
            filtered[
                [
                    "company_id",
                    "peer_percentile_score",
                    "sector_quality_score",
                    "composite_quality_score",
                ]
            ].head()
        )

        print(f"\nCompanies returned: {len(filtered)}")
        
    export_screener_results(results, config)


if __name__ == "__main__":
    main()