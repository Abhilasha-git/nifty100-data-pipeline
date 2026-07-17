CREATE TABLE IF NOT EXISTS companies (
    id TEXT PRIMARY KEY,
    company_logo TEXT,
    company_name TEXT,
    chart_link TEXT,
    about_company TEXT,
    website TEXT,
    nse_profile TEXT,
    bse_profile TEXT,
    face_value REAL,
    book_value REAL,
    roce_percentage REAL,
    roe_percentage REAL
);

CREATE TABLE IF NOT EXISTS profitandloss (
    id INTEGER PRIMARY KEY,
    company_id TEXT,
    year INTEGER,
    sales REAL,
    expenses REAL,
    operating_profit REAL,
    opm_percentage REAL,
    other_income REAL,
    interest REAL,
    depreciation REAL,
    profit_before_tax REAL,
    tax_percentage REAL,
    net_profit REAL,
    eps REAL,
    dividend_payout REAL,

    FOREIGN KEY(company_id)
    REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS balancesheet (
    id INTEGER PRIMARY KEY,
    company_id TEXT,
    year INTEGER,
    equity_capital REAL,
    reserves REAL,
    borrowings REAL,
    other_liabilities REAL,
    total_liabilities REAL,
    fixed_assets REAL,
    cwip REAL,
    investments REAL,
    other_asset REAL,
    total_assets REAL,

    FOREIGN KEY(company_id)
    REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS cashflow (
    id INTEGER PRIMARY KEY,
    company_id TEXT,
    year INTEGER,
    operating_activity REAL,
    investing_activity REAL,
    financing_activity REAL,
    net_cash_flow REAL,

    FOREIGN KEY(company_id)
    REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS analysis (
    id INTEGER PRIMARY KEY,
    company_id TEXT,
    compounded_sales_growth TEXT,
    compounded_profit_growth TEXT,
    stock_price_cagr TEXT,
    roe TEXT,

    FOREIGN KEY(company_id)
    REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    company_id TEXT,
    year INTEGER,
    annual_report TEXT,

    FOREIGN KEY(company_id)
    REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS prosandcons (
    id INTEGER PRIMARY KEY,
    company_id TEXT,
    pros TEXT,
    cons TEXT,

    FOREIGN KEY(company_id)
    REFERENCES companies(id)
);