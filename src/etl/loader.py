# src/etl/loader.py

from pathlib import Path
import pandas as pd
from src.etl.normaliser import normalize_year, normalize_ticker

RAW_DATA_DIR = Path("data/raw")


def load_excel(filename, sheet_name=0):
    """
    Load an Excel file from data/raw.

    Parameters:
        filename (str): Excel file name.
        sheet_name (int | str): Sheet index or sheet name.

    Returns:
        pandas.DataFrame
    """
    file_path = RAW_DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=1
    )

    # Clean column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Remove completely empty rows and columns
    df = df.dropna(how="all").dropna(axis=1, how="all")
    
    
    # Apply your validated normalizers
    if "year" in df.columns:
        df["year"] = df["year"].apply(normalize_year)
        
    if "ticker" in df.columns:
        df["ticker"] = df["ticker"].apply(normalize_ticker)
        
    return df

def load_core_files():
    """
    Load all 7 core Excel datasets into a dictionary of DataFrames.
    """

    files = {
        "companies": "companies.xlsx",
        "profitandloss": "profitandloss.xlsx",
        "balancesheet": "balancesheet.xlsx",
        "cashflow": "cashflow.xlsx",
        "analysis": "analysis.xlsx",
        "documents": "documents.xlsx",
        "prosandcons": "prosandcons.xlsx",
    }

    datasets = {}

    for name, filename in files.items():
        datasets[name] = load_excel(filename)

    return datasets