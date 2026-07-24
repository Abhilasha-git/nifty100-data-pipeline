import pandas as pd
import numpy as np

def winsorize(series):

    s = pd.to_numeric(series, errors="coerce")

    p10 = s.quantile(0.10)
    p90 = s.quantile(0.90)

    return s.clip(lower=p10, upper=p90)

def normalize(series, reverse=False):

    s = winsorize(series)

    minimum = s.min()
    maximum = s.max()

    if pd.isna(minimum) or pd.isna(maximum):
        return pd.Series(0, index=s.index)

    if maximum == minimum:
        return pd.Series(100, index=s.index)

    if reverse:
        return ((maximum - s) / (maximum - minimum)) * 100

    return ((s - minimum) / (maximum - minimum)) * 100


    

def calculate_composite_score(df):

    df = df.copy()
    
    roe = normalize(df["return_on_equity_pct"]).fillna(0)

    roce = normalize(df["return_on_capital_employed_pct"]).fillna(0)

    npm = normalize(df["net_profit_margin_pct"]).fillna(0)
    
    fcf = normalize(df["free_cash_flow_cr"]).fillna(0)

    cfo = normalize(df["cfo_pat_ratio"]).fillna(0)

    positive_fcf = (
        (df["free_cash_flow_cr"] > 0)
        .astype(float)
        * 100
    )
    
    rev = normalize(df["revenue_cagr_5yr"]).fillna(0)

    pat = normalize(df["pat_cagr_5yr"]).fillna(0)
    
    debt = normalize(
        df["debt_to_equity"],
        reverse=True      # lower debt is better
    ).fillna(0)

    icr = normalize(
        df["interest_coverage"]
    ).fillna(0)
    
    df["composite_quality_score"] = (
        roe * 0.15 +
        roce * 0.10 +
        npm * 0.10 +
        fcf * 0.15 +
        cfo * 0.10 +
        positive_fcf * 0.05 +
        rev * 0.10 +
        pat * 0.10 +
        debt * 0.10 +
        icr * 0.05
    ).fillna(0)
        
    # Sector-relative normalization
    sector_min = df.groupby("broad_sector")["composite_quality_score"].transform("min")
    sector_max = df.groupby("broad_sector")["composite_quality_score"].transform("max")

    df["sector_quality_score"] = np.where(
        sector_max == sector_min,
        100,
        (
            (df["composite_quality_score"] - sector_min)
            / (sector_max - sector_min)
        ) * 100,
    )
    df["sector_quality_score"] = (
        df["sector_quality_score"].fillna(0)
    )

    print(df.columns.tolist())
    
    print(
        df[df["composite_quality_score"].isna()][
            ["company_id", "year"]
            ]
        )
    return df.sort_values(
        "sector_quality_score",
        ascending=False
    )