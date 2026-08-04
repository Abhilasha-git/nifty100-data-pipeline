import streamlit as st
import plotly.express as px

from utils.db import (
    get_companies,
    get_market_cap,
    get_pl,
    get_ratios,
)

st.title("🏭 Sector Analysis")

companies = get_companies()

sector = st.selectbox(
    "Select Sector",
    sorted(companies["broad_sector"].dropna().unique())
)

year = st.selectbox(
    "Financial Year",
    [2024, 2023, 2022, 2021, 2020, 2019],
    index=0,
)

sector_companies = companies[
    companies["broad_sector"] == sector
]

marketcap = get_market_cap(year)

rows = []

for ticker in sector_companies["company_id"]:

    pl = get_pl(ticker)
    pl = pl[pl["year"] == year]

    ratios = get_ratios(ticker, year)

    if pl.empty or ratios.empty:
        continue

    mc = marketcap[
        marketcap["company_id"] == ticker
    ]

    if mc.empty:
        continue

    rows.append({

        "Company": ticker,

        "Revenue": pl.iloc[0]["sales"],

        "ROE": ratios.iloc[0]["return_on_equity_pct"],

        "Market Cap": mc.iloc[0]["market_cap_crore"],

        "Sub Sector": sector_companies[
            sector_companies.company_id == ticker
        ].iloc[0]["sub_sector"]

    })

df = __import__("pandas").DataFrame(rows)

st.subheader("Sector Bubble Chart")

fig = px.scatter(

    df,

    x="Revenue",

    y="ROE",

    size="Market Cap",

    color="Sub Sector",

    hover_name="Company",

    size_max=60,

)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Sector Median KPIs")

metrics = {

    "Median ROE": df["ROE"].median(),

    "Median Revenue": df["Revenue"].median(),

    "Median Market Cap": df["Market Cap"].median(),

}

bar = px.bar(

    x=list(metrics.keys()),

    y=list(metrics.values()),

    labels={"x": "", "y": ""},

)

st.plotly_chart(bar, use_container_width=True)