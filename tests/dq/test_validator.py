import pandas as pd

from src.etl.validator import DataValidator


def make_validator(datasets):
    validator = DataValidator.__new__(DataValidator)
    validator.datasets = datasets
    validator.failures = []
    return validator


def failure_rules(validator):
    return [failure["rule"] for failure in validator.failures]


def test_dq01_duplicate_company_id():
    datasets = {
        "companies": pd.DataFrame({
            "id": [1, 1, 2],
        })
    }

    validator = make_validator(datasets)
    validator.dq01_primary_key()

    assert failure_rules(validator) == ["DQ-01", "DQ-01"]


def test_dq02_duplicate_company_year():
    datasets = {
        "profitandloss": pd.DataFrame({
            "company_id": [1, 1, 2],
            "year": [2025, 2025, 2025],
        })
    }

    validator = make_validator(datasets)
    validator.dq02_company_year()

    assert failure_rules(validator) == ["DQ-02", "DQ-02"]


def test_dq03_invalid_foreign_key():
    datasets = {
        "companies": pd.DataFrame({"id": [1, 2]}),
        "profitandloss": pd.DataFrame({"company_id": [1, 99]}),
        "balancesheet": pd.DataFrame({"company_id": [1]}),
        "cashflow": pd.DataFrame({"company_id": [1]}),
        "analysis": pd.DataFrame({"company_id": [1]}),
        "documents": pd.DataFrame({"company_id": [1]}),
        "prosandcons": pd.DataFrame({"company_id": [1]}),
    }

    validator = make_validator(datasets)
    validator.dq03_foreign_keys()

    assert failure_rules(validator) == ["DQ-03"]


def test_dq04_balance_sheet_mismatch():
    datasets = {
        "balancesheet": pd.DataFrame({
            "company_id": [1],
            "year": [2025],
            "total_assets": [1000],
            "total_liabilities": [900],
        })
    }

    validator = make_validator(datasets)
    validator.dq04_balance_sheet()

    assert failure_rules(validator) == ["DQ-04"]
    assert validator.failures[0]["severity"] == "WARNING"


def test_dq05_operating_margin_mismatch():
    datasets = {
        "profitandloss": pd.DataFrame({
            "company_id": [1],
            "year": [2025],
            "sales": [1000],
            "operating_profit": [200],
            "opm_percentage": [10],
        })
    }

    validator = make_validator(datasets)
    validator.dq05_operating_margin()

    assert failure_rules(validator) == ["DQ-05"]


def test_dq06_non_positive_sales():
    datasets = {
        "profitandloss": pd.DataFrame({
            "company_id": [1],
            "year": [2025],
            "sales": [0],
        })
    }

    validator = make_validator(datasets)
    validator.dq06_positive_sales()

    assert failure_rules(validator) == ["DQ-06"]


def test_dq07_net_cash_flow_mismatch():
    datasets = {
        "cashflow": pd.DataFrame({
            "company_id": [1],
            "year": [2025],
            "operating_activity": [100],
            "investing_activity": [-20],
            "financing_activity": [-10],
            "net_cash_flow": [999],
        })
    }

    validator = make_validator(datasets)
    validator.dq07_net_cash_flow()

    assert failure_rules(validator) == ["DQ-07"]


def test_dq08_invalid_tax_rate():
    datasets = {
        "profitandloss": pd.DataFrame({
            "company_id": [1],
            "year": [2025],
            "tax_percentage": [101],
        })
    }

    validator = make_validator(datasets)
    validator.dq08_tax_rate()

    assert failure_rules(validator) == ["DQ-08"]


def test_dq09_invalid_dividend_payout():
    datasets = {
        "profitandloss": pd.DataFrame({
            "company_id": [1],
            "year": [2025],
            "dividend_payout": [-1],
        })
    }

    validator = make_validator(datasets)
    validator.dq09_dividend_payout()

    assert failure_rules(validator) == ["DQ-09"]


def test_dq10_invalid_url():
    datasets = {
        "companies": pd.DataFrame({
            "id": [1],
            "website": ["not-a-url"],
        }),
        "documents": pd.DataFrame({
            "company_id": [1],
            "annual_report": ["https://example.com/report.pdf"],
        }),
    }

    validator = make_validator(datasets)
    validator.dq10_url_validation()

    assert failure_rules(validator) == ["DQ-10"]


def test_dq11_eps_sign_mismatch():
    datasets = {
        "profitandloss": pd.DataFrame({
            "company_id": [1],
            "year": [2025],
            "net_profit": [-100],
            "eps": [5],
        })
    }

    validator = make_validator(datasets)
    validator.dq11_eps_sign()

    assert failure_rules(validator) == ["DQ-11"]


def test_dq12_invalid_year():
    datasets = {
        "profitandloss": pd.DataFrame({
            "company_id": [1],
            "year": [1999],
        }),
        "balancesheet": pd.DataFrame({
            "company_id": [1],
            "year": [2025],
        }),
        "cashflow": pd.DataFrame({
            "company_id": [1],
            "year": [2025],
        }),
        "documents": pd.DataFrame({
            "company_id": [1],
            "year": [2025],
        }),
    }

    validator = make_validator(datasets)
    validator.dq12_year_coverage()

    assert failure_rules(validator) == ["DQ-12"]


def test_dq13_duplicate_documents():
    datasets = {
        "documents": pd.DataFrame({
            "company_id": [1, 1],
            "year": [2025, 2025],
            "annual_report": ["https://example.com/a.pdf"] * 2,
        })
    }

    validator = make_validator(datasets)
    validator.dq13_duplicate_documents()

    assert failure_rules(validator) == ["DQ-13", "DQ-13"]


def test_dq14_missing_mandatory_field():
    datasets = {
        "companies": pd.DataFrame({
            "id": [1],
            "company_name": [None],
            "website": ["https://example.com"],
        })
    }

    validator = make_validator(datasets)
    validator.dq14_mandatory_fields()

    assert failure_rules(validator) == ["DQ-14"]


def test_dq15_invalid_numeric_range():
    datasets = {
        "companies": pd.DataFrame({
            "id": [1],
            "roe_percentage": [150],
            "roce_percentage": [20],
        })
    }

    validator = make_validator(datasets)
    validator.dq15_numeric_ranges()

    assert failure_rules(validator) == ["DQ-15"]


def test_dq16_empty_dataset():
    datasets = {
        "companies": pd.DataFrame({"id": [1]}),
        "profitandloss": pd.DataFrame(),
        "balancesheet": pd.DataFrame({"id": [1]}),
        "cashflow": pd.DataFrame({"id": [1]}),
        "analysis": pd.DataFrame({"id": [1]}),
        "documents": pd.DataFrame({"id": [1]}),
        "prosandcons": pd.DataFrame({"id": [1]}),
    }

    validator = make_validator(datasets)
    validator.dq16_dataset_completeness()

    assert failure_rules(validator) == ["DQ-16"]
    assert validator.failures[0]["severity"] == "CRITICAL"
