import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from utils.db import (
    get_peers,
    get_companies,
    get_ratios,
)

st.title("🤝 Peer Comparison")

companies = get_companies()

peer_groups = [
    "IT Services",
    "Banks",
    "Pharmaceuticals",
    "FMCG",
    "Energy",
    "Auto",
    "Metals",
    "Capital Goods",
    "Consumer",
    "Telecom",
    "Insurance",
]

peer_group = st.selectbox(
    "Peer Group",
    peer_groups,
)

peer_df = get_peers(peer_group)

if peer_df.empty:
    st.warning("No companies available.")
    st.stop()

company = st.selectbox(
    "Benchmark Company",
    peer_df["company_id"].unique(),
)

st.subheader("Peer Comparison Table")

st.dataframe(
    peer_df,
    use_container_width=True,
)

metrics = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "free_cash_flow_cr",
]

company_ratios = get_ratios(company)

company_latest = (
    company_ratios
    .dropna(subset=["year"])
    .sort_values("year")
    .iloc[-1]
)

peer_values = []

for metric in metrics:

    vals = []

    for ticker in peer_df["company_id"]:

        r = get_ratios(ticker)

        r = r.dropna(subset=["year"])

        if len(r):

            vals.append(
                r.sort_values("year").iloc[-1][metric]
            )

    peer_values.append(pd.Series(vals).mean())

company_values = [
    company_latest[m]
    for m in metrics
]

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=company_values,
        theta=metrics,
        fill="toself",
        name=company,
    )
)

fig.add_trace(
    go.Scatterpolar(
        r=peer_values,
        theta=metrics,
        fill="toself",
        name="Peer Average",
    )
)

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True)),
    showlegend=True,
)

st.subheader("Radar Comparison")

st.plotly_chart(
    fig,
    use_container_width=True,
)