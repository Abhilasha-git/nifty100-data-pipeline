import sqlite3
import pandas as pd

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    interest_coverage,
    asset_turnover
)

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    capex_intensity,
    fcf_conversion_rate,
    cfo_quality_score,
    capital_allocation_pattern
)

from src.analytics.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr
)

DB_PATH = "db/nifty100.db"


def load_tables():
    conn = sqlite3.connect(DB_PATH)

    pnl = pd.read_sql("SELECT * FROM profitandloss", conn)
    bs = pd.read_sql("SELECT * FROM balancesheet", conn)
    cf = pd.read_sql("SELECT * FROM cashflow", conn)

    conn.close()

    return pnl, bs, cf

def build_dataframe():

    pnl, bs, cf = load_tables()

    df = pnl.merge(
        bs,
        on=["company_id", "year"],
        how="left"
    )

    df = df.merge(
        cf,
        on=["company_id", "year"],
        how="left"
    )

    return df

def compute_ratios(df):

    # Profitability
    df["net_profit_margin_pct"] = df.apply(
        lambda x: net_profit_margin(
            x["net_profit"],
            x["sales"]
        ),
        axis=1
    )

    df["operating_profit_margin_pct"] = df.apply(
        lambda x: operating_profit_margin(
            x["operating_profit"],
            x["sales"]
        ),
        axis=1
    )

    df["return_on_equity_pct"] = df.apply(
        lambda x: return_on_equity(
            x["net_profit"],
            x["equity_capital"],
            x["reserves"]
        ),
        axis=1
    )

    df["return_on_capital_employed_pct"] = df.apply(
        lambda x: return_on_capital_employed(
            x["operating_profit"],
            x["other_income"],
            x["equity_capital"],
            x["reserves"],
            x["borrowings"]
        ),
        axis=1
    )

    df["return_on_assets_pct"] = df.apply(
        lambda x: return_on_assets(
            x["net_profit"],
            x["total_assets"]
        ),
        axis=1
    )

    # Leverage
    df["debt_to_equity"] = df.apply(
        lambda x: debt_to_equity(
            x["borrowings"],
            x["equity_capital"],
            x["reserves"]
        ),
        axis=1
    )

    df["interest_coverage"] = df.apply(
        lambda x: interest_coverage(
            x["operating_profit"],
            x["other_income"],
            x["interest"]
        ),
        axis=1
    )

    df["asset_turnover"] = df.apply(
        lambda x: asset_turnover(
            x["sales"],
            x["total_assets"]
        ),
        axis=1
    )

    # Cash Flow
    df["free_cash_flow_cr"] = df.apply(
        lambda x: free_cash_flow(
            x["operating_activity"],
            x["investing_activity"]
        ),
        axis=1
    )

    df["capex_intensity_pct"] = df.apply(
        lambda x: capex_intensity(
            x["investing_activity"],
            x["sales"]
        )[1],
        axis=1
    )

    df["fcf_conversion_rate_pct"] = df.apply(
        lambda x: fcf_conversion_rate(
            x["free_cash_flow_cr"],
            x["operating_profit"]
        ),
        axis=1
    )
    
    # CFO Quality (current year ratio)
    df["cfo_pat_ratio"] = (
        df["operating_activity"] / df["net_profit"]
    )

    df["cfo_quality_label"] = df["cfo_pat_ratio"].apply(
        lambda x:
            "High Quality" if x > 1
            else "Moderate" if x >= 0.5
            else "Accrual Risk"
    )
    
    df["capital_allocation_pattern"] = df.apply(
        lambda x: capital_allocation_pattern(
            x["operating_activity"],
            x["investing_activity"],
            x["financing_activity"],
            x["cfo_pat_ratio"]
        ),
        axis=1
    )

    return df

def save_to_database(df):

    conn = sqlite3.connect(DB_PATH)

    columns = [
        "company_id",
        "year",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "return_on_assets_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "capex_intensity_pct",
        "fcf_conversion_rate_pct",
        "cfo_pat_ratio",
        "cfo_quality_label",
        "capital_allocation_pattern",
    ]

    output = df[columns].copy()

    output.to_sql(
        "financial_ratios",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print(f"Saved {len(output)} rows to financial_ratios table.")

def main():

    df = build_dataframe()

    df = compute_ratios(df)

    save_to_database(df)

    print(
        df[
            [
                "company_id",
                "year",
                "net_profit_margin_pct",
                "return_on_equity_pct",
                "debt_to_equity",
                "free_cash_flow_cr"
            ]
        ].head()
    )

if __name__ == "__main__":
    main()