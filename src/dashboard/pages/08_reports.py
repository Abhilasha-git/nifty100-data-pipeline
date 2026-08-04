import streamlit as st
import requests

from utils.db import get_companies, get_reports

st.title("📄 Annual Reports")

companies = get_companies()

company = st.selectbox(
    "Select Company",
    companies["company_name"],
)

ticker = companies.loc[
    companies["company_name"] == company,
    "company_id",
].iloc[0]

reports = get_reports(ticker)

if reports.empty:
    st.warning("No reports available.")
    st.stop()

st.subheader(f"{company} Annual Reports")

for _, row in reports.iterrows():

    year = int(row["year"])
    url = row["annual_report"]

    if url and str(url).startswith("http"):
        st.markdown(
            f"📄 **{year}** — [Open Annual Report]({url})"
        )
    else:
        st.error(f"{year} — Report unavailable")