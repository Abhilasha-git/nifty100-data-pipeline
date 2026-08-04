import streamlit as st
import plotly.graph_objects as go

from utils.db import get_companies, get_ratios

st.title("📈 Trend Analysis")

companies = get_companies()

company = st.selectbox(
    "Select Company",
    companies["company_name"]
)

ticker = companies.loc[
    companies["company_name"] == company,
    "company_id"
].iloc[0]

metrics = {
    "ROE": "return_on_equity_pct",
    "ROCE": "return_on_capital_employed_pct",
    "Net Profit Margin": "net_profit_margin_pct",
    "Debt/Equity": "debt_to_equity",
    "Revenue CAGR": "revenue_cagr_5yr",
    "PAT CAGR": "pat_cagr_5yr",
    "Free Cash Flow": "free_cash_flow_cr",
}

selected = st.multiselect(
    "Select up to 3 metrics",
    list(metrics.keys()),
    default=["ROE"],
    max_selections=3,
)

df = get_ratios(ticker)

df = df.dropna(subset=["year"]).sort_values("year")

st.write(df.head())

fig = go.Figure()

for metric in selected:

    col = metrics[metric]

    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df[col],
            mode="lines+markers",
            name=metric,
        )
    )

    # YoY annotations
    for i in range(1, len(df)):

        prev = df.iloc[i - 1][col]
        curr = df.iloc[i][col]

        if prev not in [0, None] and str(prev) != "nan":

            yoy = ((curr - prev) / abs(prev)) * 100

            fig.add_annotation(
                x=df.iloc[i]["year"],
                y=curr,
                text=f"{yoy:.0f}%",
                showarrow=False,
                font=dict(size=9),
            )

fig.update_layout(
    xaxis_title="Year",
    legend_title="Metrics",
)

st.plotly_chart(
    fig,
    use_container_width=True,
)