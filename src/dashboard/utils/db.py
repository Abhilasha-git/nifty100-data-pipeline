import sqlite3

import pandas as pd
import streamlit as st

DB_PATH = "db/nifty100.db"


@st.cache_data(ttl=600)
def get_companies():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            id AS company_id,
            company_name,
            about_company
        FROM companies
        ORDER BY company_name
        """,
        conn,
    )

    conn.close()

    sectors = pd.read_excel(
        "data/raw/supporting_datasets/sectors.xlsx"
    )[["company_id", "broad_sector", "sub_sector"]]

    df = df.merge(sectors, on="company_id", how="left")

    return df


@st.cache_data(ttl=600)
def get_ratios(ticker=None, year=None):
    conn = sqlite3.connect(DB_PATH)

    conditions = []
    params = []

    if ticker is not None:
        conditions.append("company_id = ?")
        params.append(ticker)

    if year is not None:
        conditions.append("year = ?")
        params.append(year)

    query = "SELECT * FROM financial_ratios WHERE year IS NOT NULL"
    if conditions:
        query += " AND " + " AND ".join(conditions)
    query += " ORDER BY year"

    df = pd.read_sql(query, conn, params=params)
    conn.close()

    # These columns are stored as TEXT in SQLite despite holding numeric
    # values (only populated once a company has 5 years of history —
    # otherwise NULL). Coerce so pandas treats them as numbers.
    text_numeric_cols = ["revenue_cagr_5yr", "pat_cagr_5yr", "eps_cagr_5yr"]
    for col in text_numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


@st.cache_data(ttl=600)
def get_pl(ticker):
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM profitandloss
        WHERE company_id = ? AND year IS NOT NULL
        ORDER BY year
        """,
        conn,
        params=[ticker],
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_bs(ticker):
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id = ? AND year IS NOT NULL
        ORDER BY year
        """,
        conn,
        params=[ticker],
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_cf(ticker):
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM cashflow
        WHERE company_id = ? AND year IS NOT NULL
        ORDER BY year
        """,
        conn,
        params=[ticker],
    )

    conn.close()

    return df



@st.cache_data(ttl=600)
def get_sectors():

    return pd.read_excel(
        "data/raw/supporting_datasets/sectors.xlsx"
    )


@st.cache_data(ttl=600)
def get_peers(group_name):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM peer_percentiles
        WHERE peer_group_name = ?
        """,
        conn,
        params=[group_name],
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_valuation(ticker):
    return pd.DataFrame()

@st.cache_data(ttl=600)
def get_pros_cons(ticker):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT pros, cons
    FROM prosandcons
    WHERE company_id = ?
    """

    df = pd.read_sql(query, conn, params=[ticker])

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_market_cap(year):

    df = pd.read_excel(
        "data/raw/supporting_datasets/market_cap.xlsx"
    )

    return df[df["year"] == year]

@st.cache_data(ttl=600)
def get_capital_patterns(year):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            company_id,
            capital_allocation_pattern,
            free_cash_flow_cr,
            return_on_equity_pct
        FROM financial_ratios
        WHERE year = ?
        """,
        conn,
        params=[year],
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_reports(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT year, annual_report
        FROM documents
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        conn,
        params=[ticker],
    )

    conn.close()

    return df