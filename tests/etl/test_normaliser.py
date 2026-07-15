import pytest

from src.etl.normaliser import normalize_year, normalize_ticker


# ---------- normalize_year tests ----------

def test_year_integer():
    assert normalize_year(2026) == 2026


def test_year_string():
    assert normalize_year("2026") == 2026


def test_year_float_string():
    assert normalize_year("2026.0") == 2026


def test_year_fy_short():
    assert normalize_year("FY25") == 2025


def test_year_fy_long():
    assert normalize_year("FY2025") == 2025


def test_year_range():
    assert normalize_year("2025-26") == 2025


def test_year_none():
    assert normalize_year(None) is None


def test_year_empty():
    assert normalize_year("") is None


# ---------- normalize_ticker tests ----------

def test_ticker_ns():
    assert normalize_ticker("RELIANCE.NS") == "RELIANCE"


def test_ticker_bo():
    assert normalize_ticker("INFY.BO") == "INFY"


def test_ticker_upper():
    assert normalize_ticker("TCS") == "TCS"


def test_ticker_lower():
    assert normalize_ticker("tcs") == "TCS"


def test_ticker_spaces():
    assert normalize_ticker("  hdfc bank  ") == "HDFC BANK"


def test_ticker_none():
    assert normalize_ticker(None) is None