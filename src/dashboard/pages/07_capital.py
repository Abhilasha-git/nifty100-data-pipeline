import streamlit as st
import plotly.express as px

from utils.db import get_capital_patterns

st.title("💰 Capital Allocation Map")

year = st.selectbox(
    "Year",
    [2024, 2023, 2022, 2021, 2020, 2019],
    index=0,
)

df = get_capital_patterns(year)

df = df.dropna(subset=["capital_allocation_pattern"])

st.subheader("Capital Allocation Treemap")

df["size"] = 1

fig = px.treemap(
    df,
    path=["capital_allocation_pattern", "company_id"],
    values="size",
    color="return_on_equity_pct",
    color_continuous_scale="Greens",
) 

st.plotly_chart(fig, use_container_width=True)

st.subheader("Companies by Pattern")

pattern = st.selectbox(
    "Capital Allocation Pattern",
    sorted(df["capital_allocation_pattern"].unique())
)

filtered = df[df["capital_allocation_pattern"] == pattern]

st.dataframe(
    filtered[
        [
            "company_id",
            "free_cash_flow_cr",
            "return_on_equity_pct",
        ]
    ],
    use_container_width=True,
)
