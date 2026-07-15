import pytest
from src.etl.loader import load_excel


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        load_excel("missing.xlsx")