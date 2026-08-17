# src/etl/normaliser.py

import re


def normalize_year(year_val):
    if year_val is None:
        return None

    if isinstance(year_val, int):
        return year_val

    # Handle floats like 2024.0
    if isinstance(year_val, float):
        if year_val != year_val:  # NaN
            return None
        if year_val.is_integer():
            return int(year_val)

    val = str(year_val).strip().upper()

    if not val or val == "NAN":
        return None

    # TTM is not a financial year
    if val == "TTM":
        return None

    # FY24 / FY2024
    match = re.fullmatch(r"FY[- ]?(\d{2}|\d{4})", val)
    if match:
        year = int(match.group(1))
        return 2000 + year if year < 100 else year

    # Formats such as:
    # Mar 2024
    # Mar-2024
    # Mar-24
    # Dec 2013
    match = re.search(r"(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[ -]?(\d{2}|\d{4})", val)

    if match:
        year = int(match.group(1))
        return 2000 + year if year < 100 else year
    
    # Float-formatted year strings such as:
    # "2024.0"
    match = re.fullmatch(r"(\d{4})\.0+", val)
    if match:
        return int(match.group(1))

    # Financial year ranges such as:
    # "2025-26"
    match = re.fullmatch(r"(\d{4})-\d{2}", val)
    if match:
        return int(match.group(1))

    # Plain 4-digit year
    match = re.fullmatch(r"\d{4}", val)
    if match:
        return int(val)

    return None


def normalize_ticker(ticker_val):
    if ticker_val is None:
        return None

    ticker = str(ticker_val).strip().upper()

    ticker = re.sub(r"\.(NS|BO)$", "", ticker)

    return ticker