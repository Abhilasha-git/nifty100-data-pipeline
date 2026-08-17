from pathlib import Path

import pandas as pd


CASHFLOW_FILE = Path("data/raw/cashflow.xlsx")


def test_tvsmotor_mar_2022_cashflow_reconciles():
    df = pd.read_excel(CASHFLOW_FILE, header=1)

    row = df[
        (df["company_id"] == "TVSMOTOR")
        & (df["year"] == "Mar 2022")
    ]

    assert len(row) == 1, "Expected exactly one TVSMOTOR Mar 2022 row"

    record = row.iloc[0]

    calculated = (
        record["operating_activity"]
        + record["investing_activity"]
        + record["financing_activity"]
    )

    assert record["net_cash_flow"] == calculated
    assert record["net_cash_flow"] == -128


def test_cashflow_has_no_large_reconciliation_anomalies():
    df = pd.read_excel(CASHFLOW_FILE, header=1)

    calculated = (
        df["operating_activity"]
        + df["investing_activity"]
        + df["financing_activity"]
    )

    difference = (df["net_cash_flow"] - calculated).abs()

    assert (difference > 1).sum() == 0