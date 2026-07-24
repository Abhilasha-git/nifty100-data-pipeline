import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"


METRICS = {
    "ROE": "return_on_equity_pct",
    "ROCE": "return_on_capital_employed_pct",
    "Net Profit Margin": "net_profit_margin_pct",
    "Debt to Equity": "debt_to_equity",
    "Free Cash Flow": "free_cash_flow_cr",
    "PAT CAGR 5Y": "pat_cagr_5yr",
    "Revenue CAGR 5Y": "revenue_cagr_5yr",
    "EPS CAGR 5Y": "eps_cagr_5yr",
    "Interest Coverage": "interest_coverage",
    "Asset Turnover": "asset_turnover",
}

def load_data():

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn,
    )

    peer = pd.read_excel(
        "data/raw/supporting_datasets/peer_groups.xlsx"
    )

    conn.close()

    return ratios, peer

def merge_peer_groups():

    ratios, peer = load_data()

    df = ratios.merge(
        peer[
            [
                "company_id",
                "peer_group_name",
            ]
        ],
        on="company_id",
        how="left",
    )

    return df

def calculate_peer_percentiles():

    df = merge_peer_groups()

    missing = df[df["peer_group_name"].isna()]

    if not missing.empty:
        print(
            f"No peer group assigned for {missing['company_id'].nunique()} companies."
    )
    # Ignore companies without peer groups
    df = df[df["peer_group_name"].notna()].copy()

    rows = []

    metrics = {
        "ROE": ("return_on_equity_pct", False),
        "ROCE": ("return_on_capital_employed_pct", False),
        "Net Profit Margin": ("net_profit_margin_pct", False),
        "Debt to Equity": ("debt_to_equity", True),
        "Free Cash Flow": ("free_cash_flow_cr", False),
        "PAT CAGR 5Y": ("pat_cagr_5yr", False),
        "Revenue CAGR 5Y": ("revenue_cagr_5yr", False),
        "EPS CAGR 5Y": ("eps_cagr_5yr", False),
        "Interest Coverage": ("interest_coverage", False),
        "Asset Turnover": ("asset_turnover", False),
    }

    for (group_name, year), group in df.groupby(
        ["peer_group_name", "year"]
    ):

        for metric_name, (column, inverse) in metrics.items():

            values = pd.to_numeric(group[column], errors="coerce")

            ranks = values.rank(pct=True)

            if inverse:
                ranks = 1 - ranks

            for idx in group.index:

                rows.append({
                    "company_id": group.loc[idx, "company_id"],
                    "peer_group_name": group_name,
                    "metric": metric_name,
                    "value": group.loc[idx, column],
                    "percentile_rank": ranks.loc[idx] * 100,
                    "year": group.loc[idx, "year"],
                })

    return pd.DataFrame(rows)

def save_peer_percentiles(df):

    conn = sqlite3.connect(DB_PATH)

    df.to_sql(
        "peer_percentiles",
        conn,
        if_exists="replace",
        index=False,
    )

    conn.close()

if __name__ == "__main__":

    result = calculate_peer_percentiles()

    print(result.head())

    print()

    print("Rows:", len(result))

    save_peer_percentiles(result)

    print("Saved to peer_percentiles table.")