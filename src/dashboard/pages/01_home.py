import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import get_ratios, get_companies

st.title("🏠 Home Dashboard")

st.sidebar.subheader("Filters")
selected_year = st.sidebar.selectbox(
    "Year",
    options=[2024, 2023, 2022, 2021, 2020, 2019],
    index=0,
)

ratios = get_ratios(None, year=selected_year)
companies = get_companies()

# KPI calculations
average_roe = round(ratios["return_on_equity_pct"].median(), 2)
median_roce = round(ratios["return_on_capital_employed_pct"].median(), 2)
median_de = round(ratios["debt_to_equity"].median(), 2)
median_revenue_cagr = round(ratios["revenue_cagr_5yr"].median(), 2)
total_companies = companies.shape[0]
debt_free = (ratios["debt_to_equity"] == 0).sum()

st.subheader(f"Summary KPIs — FY{selected_year}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("average ROE", f"{average_roe:.2f}%")
with col2:
    st.metric("Median ROCE", f"{median_roce:.2f}%")
with col3:
    st.metric("Median D/E", f"{median_de:.2f}")

col4, col5, col6 = st.columns(3)
with col4:
    st.metric("Total Companies", total_companies)
with col5:
    st.metric("Median Revenue CAGR (5Y)", f"{median_revenue_cagr:.2f}%")
with col6:
    st.metric("Debt-Free Companies", debt_free)

# --- Sector breakdown donut chart ---
st.subheader("Sector Breakdown")

sector_counts = companies["broad_sector"].value_counts().reset_index()
sector_counts.columns = ["broad_sector", "count"]

fig = px.pie(
    sector_counts,
    names="broad_sector",
    values="count",
    hole=0.5,
)
fig.update_layout(showlegend=True)
st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Top 5 Quality Companies")

top5 = ratios[
    [
        "company_id",
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "debt_to_equity",
    ]
].copy()

top5["Quality Score"] = (
    top5["return_on_equity_pct"]
    + top5["return_on_capital_employed_pct"]
    - (top5["debt_to_equity"] * 10)
)

top5 = top5.sort_values(
    by="Quality Score",
    ascending=False,
).head(5)

top5 = top5.merge(
    companies[["company_id", "company_name"]],
    on="company_id",
    how="left",
)

top5 = top5[
    [
        "company_id",
        "company_name",
        "Quality Score",
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "debt_to_equity",
    ]
]

st.dataframe(
    top5,
    use_container_width=True,
)