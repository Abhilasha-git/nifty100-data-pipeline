import streamlit as st
import pandas as pd

from utils.db import get_ratios, get_companies

st.title("🔍 Stock Screener")

companies = get_companies()
ratios = get_ratios()

latest = (
    ratios
    .sort_values("year")
    .groupby("company_id")
    .tail(1)
)

df = latest.merge(
    companies,
    on="company_id",
    how="left",
)

st.sidebar.header("Filters")

st.sidebar.subheader("Quick Presets")

preset = st.sidebar.radio(
    "Choose a preset",
    [
        "Custom",
        "Quality",
        "Value",
        "Growth",
        "Dividend",
        "Debt-Free",
        "Turnaround",
    ],
)

if preset == "Quality":
    roe_min = 20
    de_max = 0.5

elif preset == "Value":
    roe_min = 10
    de_max = 1.0

elif preset == "Growth":
    revenue_cagr_min = 15
    pat_cagr_min = 15

elif preset == "Dividend":
    dividend_min = 1

elif preset == "Debt-Free":
    de_max = 0

elif preset == "Turnaround":
    revenue_cagr_min = 0

roe_min = st.sidebar.slider("ROE Min (%)", 0, 50, 15)

de_max = st.sidebar.slider("Debt/Equity Max", 0.0, 5.0, 1.0)

fcf_min = st.sidebar.slider("FCF Min (Cr)", -10000, 50000, 0)

revenue_cagr_min = st.sidebar.slider("Revenue CAGR Min (%)", -20, 50, 5)

pat_cagr_min = st.sidebar.slider("PAT CAGR Min (%)", -20, 50, 5)

opm_min = st.sidebar.slider("OPM Min (%)", 0, 60, 15)

pe_max = st.sidebar.slider("P/E Max", 0, 100, 40)

pb_max = st.sidebar.slider("P/B Max", 0, 20, 10)

dividend_min = st.sidebar.slider("Dividend Yield Min (%)", 0.0, 10.0, 0.0)

icr_min = st.sidebar.slider("Interest Coverage Min", 0, 50, 3)

roe_min = st.sidebar.slider(
    "Minimum ROE (%)",
    0,
    50,
    15,
)

de_max = st.sidebar.slider(
    "Maximum Debt/Equity",
    0.0,
    5.0,
    1.0,
)

fcf_min = st.sidebar.slider(
    "Minimum Free Cash Flow (Cr)",
    -10000,
    50000,
    0,
)

filtered = df[
    (df["return_on_equity_pct"] >= roe_min)
    &
    (df["debt_to_equity"] <= de_max)
    &
    (df["free_cash_flow_cr"] >= fcf_min)
    &
    (df["revenue_cagr_5yr"] >= revenue_cagr_min)
    &
    (df["pat_cagr_5yr"] >= pat_cagr_min)
]

st.subheader(f"{len(filtered)} Companies Match")

st.subheader(f"{len(filtered)} Companies Match")

display_df = filtered[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "return_on_equity_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
    ]
]

st.dataframe(
    display_df,
    use_container_width=True,
)

csv = display_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download CSV",
    csv,
    file_name="screener_results.csv",
    mime="text/csv",
)