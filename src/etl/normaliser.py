# src/etl/normaliser.py

import re

def normalize_year(year_val):
    if year_val is None:
        return None
    if isinstance(year_val, int):
        return year_val
    
    val_str = str(year_val).upper().strip()
    if val_str == "":
        return None
    
    # 1. Check for 'FY' pattern (uses capture group, so group(1) is correct)
    if 'FY' in val_str:
        match = re.search(r'FY(\d+)', val_str)
        if match:
            year_part = int(match.group(1))
            return (2000 + year_part) if year_part < 100 else year_part
            
    # 2. Check for standard 4-digit year (No capture group, so use group(0))
    match = re.search(r'\d{4}', val_str)
    if match:
        return int(match.group(0))
    
    return None

def normalize_ticker(ticker_val):
    if ticker_val is None:
        return None
    
    ticker = str(ticker_val).strip().upper()
    # Remove common exchange suffixes
    ticker = re.sub(r"\.(NS|BO)$", "", ticker)
    return ticker