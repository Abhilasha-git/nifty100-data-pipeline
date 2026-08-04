import streamlit as st
import plotly.graph_objects as go

from utils.db import (
    get_companies,
    get_ratios,
    get_pl,
    get_pros_cons,
)

st.title("🏢 Company Profile")

companies = get_companies()

company_names = companies["company_name"].tolist()

selected_company = st.selectbox(
    "Select Company",
    company_names,
)

company = companies[
    companies["company_name"] == selected_company
].iloc[0]

ticker = company["company_id"]

st.success(f"Selected: {selected_company}")

st.subheader("Company Information")

col1, col2 = st.columns(2)

with col1:
    st.write("**Company**")
    st.write(company["company_name"])

    st.write("**Ticker**")
    st.write(company["company_id"])

with col2:
    st.write("**Sector**")
    st.write(company["broad_sector"])

    st.write("**Sub Sector**")
    st.write(company["sub_sector"])
    
st.subheader("About Company")

about = company["about_company"]

if about and str(about).strip():
    st.write(about)
else:
    st.info("Business description not available.")

ratios = get_ratios(ticker)
ratios = ratios.dropna(subset=["year"])

latest = ratios.sort_values("year").iloc[-1]

st.subheader("Latest Financial KPIs")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("ROE", f"{latest['return_on_equity_pct']:.2f}%")
with c2:
    st.metric("ROCE", f"{latest['return_on_capital_employed_pct']:.2f}%")
with c3:
    st.metric("Net Profit Margin", f"{latest['net_profit_margin_pct']:.2f}%")

c4, c5, c6 = st.columns(3)
with c4:
    st.metric("Debt / Equity", f"{latest['debt_to_equity']:.2f}")
with c5:
    st.metric("Revenue CAGR (5Y)", f"{latest['revenue_cagr_5yr']:.2f}%")
with c6:
    st.metric("Free Cash Flow", f"{latest['free_cash_flow_cr']:.0f} Cr")

# --- Revenue & Net Profit 10-year bar chart ---
pl = get_pl(ticker)
pl = pl.dropna(subset=["year"]).sort_values("year")

st.subheader("Revenue & Net Profit (10-Year Trend)")

fig_pl = go.Figure()
fig_pl.add_trace(go.Bar(x=pl["year"], y=pl["sales"], name="Revenue"))
fig_pl.add_trace(go.Bar(x=pl["year"], y=pl["net_profit"], name="Net Profit"))
fig_pl.update_layout(barmode="group", xaxis_title="Year", yaxis_title="₹ Cr")
st.plotly_chart(fig_pl, use_container_width=True)

# --- ROE vs ROCE dual-axis line chart ---
st.subheader("ROE vs ROCE (10-Year Trend)")

ratios_all = ratios.sort_values("year")

fig_roe = go.Figure()
fig_roe.add_trace(go.Scatter(
    x=ratios_all["year"], y=ratios_all["return_on_equity_pct"],
    name="ROE (%)", yaxis="y1", mode="lines+markers"
))
fig_roe.add_trace(go.Scatter(
    x=ratios_all["year"], y=ratios_all["return_on_capital_employed_pct"],
    name="ROCE (%)", yaxis="y2", mode="lines+markers"
))
fig_roe.update_layout(
    xaxis_title="Year",
    yaxis=dict(title="ROE (%)"),
    yaxis2=dict(title="ROCE (%)", overlaying="y", side="right"),
    legend=dict(orientation="h", y=1.1),
)
st.plotly_chart(fig_roe, use_container_width=True)

st.subheader("Pros & Cons")

pc = get_pros_cons(ticker)

if not pc.empty:

    col1, col2 = st.columns(2)

    with col1:
        st.success("Pros")
        for p in str(pc.iloc[0]["pros"]).split(";"):
            if p.strip():
                st.write("✅", p.strip())

    with col2:
        st.error("Cons")
        for c in str(pc.iloc[0]["cons"]).split(";"):
            if c.strip():
                st.write("❌", c.strip())

else:
    st.info("No pros/cons available.")