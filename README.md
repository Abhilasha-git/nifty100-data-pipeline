# 📈 Nifty100 Data Pipeline

A production-style financial analytics pipeline built in Python for analyzing Nifty 100 companies. The project automates financial KPI computation, peer-group benchmarking, composite quality scoring, configurable stock screening, Excel report generation, an interactive Streamlit dashboard, and valuation analysis.

## 📌 Repository Overview

This repository provides an end-to-end financial analytics platform for **92 Nifty 100 companies**. It includes:

- 📥 Automated ETL pipeline for financial data processing
- 📊 Financial KPI computation engine
- ⭐ Composite Quality Scoring system
- 🏢 Peer benchmarking and sector analytics
- 🔍 Configurable stock screener
- 📈 Interactive 8-page Streamlit dashboard
- 💹 Valuation module with sector-relative P/E analysis
- 📄 Automated Excel reports and annual report integration

---

# 🚀 Features

---

# 🚀 Features

### 📊 Financial KPI Engine

Computes key financial metrics including:

- Return on Equity (ROE)
- Return on Capital Employed (ROCE)
- Return on Assets (ROA)
- Net Profit Margin (NPM)
- Operating Profit Margin (OPM)
- Debt-to-Equity Ratio
- Interest Coverage Ratio
- Asset Turnover Ratio
- Free Cash Flow (FCF)
- CFO/PAT Ratio
- Revenue CAGR (5 Years)
- PAT CAGR (5 Years)
- EPS CAGR (5 Years)

---

### ⭐ Composite Quality Score

Generates a weighted quality score using multiple financial indicators covering:

- Profitability
- Growth
- Capital Efficiency
- Cash Flow Quality
- Balance Sheet Strength

---

### 🏢 Peer Group Analytics

Performs peer benchmarking within industry groups by calculating:

- Metric-wise percentile rankings
- Peer percentile score
- Best performing metric
- Weakest performing metric

Current peer groups include:

- IT Services
- FMCG
- Automobiles
- Pharmaceuticals
- Power & Utilities
- Steel
- Private Banks
- Public Sector Banks
- Life Insurance
- Consumer Finance
- Oil & Gas

---

### 🔍 Stock Screener Engine

Supports analyst-editable screeners using YAML configuration.

Current presets include:

- Quality Compounder
- Value Pick
- Growth Accelerator
- Dividend Champion
- Debt Free Bluechip
- Turnaround Watch

Thresholds can be modified without changing Python source code.

---

### 📊 Interactive Streamlit Dashboard

The project now includes a production-style multi-page Streamlit dashboard for exploring all Nifty 100 companies.

Available screens:

- 🏠 Home Dashboard
- 🏢 Company Profile
- 🔍 Stock Screener
- 🤝 Peer Comparison
- 📈 Trend Analysis
- 🏭 Sector Analysis
- 💰 Capital Allocation Map
- 📄 Annual Reports

Features include:

- Financial KPI cards
- Interactive Plotly visualizations
- Company search
- Peer benchmarking
- Downloadable screener results
- Sector analysis
- Capital allocation treemap
- Annual report links

---

### 💹 Valuation Module

Automatically computes valuation metrics using market capitalization data.

Calculates:

- Free Cash Flow Yield
- Sector Median P/E
- Premium/Discount vs Sector
- Valuation Flags

Generated outputs:

output/valuation_summary.xlsx

output/valuation_flags.csv

---

### 📄 Automated Reports

The pipeline automatically generates:

### 1. Screener Workbook

```
output/screener_output.xlsx
```

Contains:

- One worksheet per screener preset
- Composite Quality Score
- Sector Quality Score
- Peer Percentile Score
- Colour-coded metrics

---

### 2. Peer Comparison Workbook

```
output/peer_comparison.xlsx
```

Contains:

- One worksheet per peer group
- Financial metrics
- Peer percentile rankings
- Conditional formatting for quick comparison

---

### 3. Radar Charts

```
reports/radar_charts/
```

Generates one radar chart for every company comparing:

- Company performance
- Peer Group Average (or Nifty 100 Average where applicable)

---

# 🏗 Project Architecture

```
nifty100-data-pipeline/
│
├── data/
│   ├── raw/
│   │   ├── companies/
│   │   ├── financial_statements/
│   │   └── supporting_datasets/
│   │       ├── peer_groups.xlsx
│   │       └── sectors.xlsx
│   │
│   └── processed/
│
├── db/
│   └── nifty100.db
│
├── docs/
│
├── notebooks/
│
├── output/
│   ├── screener_output.xlsx
│   ├── peer_comparison.xlsx
|   ├── valuation_summary.xlsx
│   └── valuation_flags.csv
│
├── reports/
│   └── radar_charts/
│
├── scripts/
│
├── src/
│   │
│   ├── analytics/
|   |
|   ├──dashboard/
│   │   ├── app.py
│   │   ├── pages/
│   │   │   ├── 01_home.py
│   │   │   ├── 02_profile.py
│   │   │   ├── 03_screener.py
│   │   │   ├── 04_peers.py
│   │   │   ├── 05_trends.py
│   │   │   ├── 06_sectors.py
│   │   │   ├── 07_capital.py
│   │   │   └── 08_reports.py
│   │   └── utils/
│   │       └── db.py
|   |
│   ├── config/
│   │   └── screener_config.yaml
│   │
│   ├── etl/
│   │   ├── loader.py
│   │   ├── normaliser.py
|   |   ├── db_loader.py
│   │   └── validator.py
│   │
│   ├── reports/
│   │   ├── peer_report.py
│   │   ├── company_report.py
│   │   └── radar.py
│   │
│   ├── scoring/
│   │   └── score_engine.py
│   │
│   ├── screener/
│   │   ├── engine.py
│   │   ├── backtest.py
│   │   └── export_excel.py
│   │
│   ├── utils/
│   │
│   └── __init__.py
│
├── tests/
│   ├── etl/
│   │   ├── test_loader.py
│   │   └── test_normaliser.py
│   │
│   └── kpi/
│       ├── test_cagr.py
│       ├── test_cashflow_kpis.py
│       ├── test_leverage.py
│       └── test_profitability.py
│
├── requirements.txt
├── pyproject.toml
├── Makefile
└── README.md
```

---

# 📁 Module Overview

| Module | Responsibility |
|---------|----------------|
| **ETL** | Data loading, normalization, validation and preprocessing |
| **Analytics** | Financial KPI calculations and peer-group analytics |
| **Scoring** | Composite Quality Score computation |
| **Screener** | Rule-based stock screening engine |
| **Reports** | Excel reports and radar chart generation |
| **Config** | YAML-based screener thresholds |
| **Tests** | Automated unit tests |

---

# 🛠 Technology Stack

- Python 3.14
- Pandas
- NumPy
- Streamlit
- Plotly
- SQLite
- OpenPyXL
- Matplotlib
- PyYAML
- Pytest

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/Abhilasha-git/nifty100-data-pipeline.git
cd nifty100-data-pipeline
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶ Running the Pipeline

Execute the complete financial analytics pipeline:

```bash
python -m src.screener.engine
```

Generated outputs:

```
output/
├── screener_output.xlsx
├── peer_comparison.xlsx
├── valuation_summary.xlsx
└── valuation_flags.csv

reports/
└── radar_charts/
```

---

# ▶ Running the Dashboard

Launch the interactive dashboard:

```bash
streamlit run src/dashboard/app.py
```

The dashboard includes:

- Home Dashboard
- Company Profile
- Stock Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation Map
- Annual Reports

---

# 🧪 Running Tests

Execute the complete test suite:

```bash
python -m pytest
```

Current Status

```
49 tests passed
```

---

# ⚙ Configuration

All screener thresholds are configurable through

```
src/config/screener_config.yaml
```

This allows analysts to modify screening rules without changing Python code.

---

# 📊 Outputs

The project generates:

- Financial KPI calculations
- Composite Quality Scores
- Peer Percentile Rankings
- Excel Screening Reports
- Peer Comparison Reports
- Radar Chart Visualizations
- Interactive Streamlit dashboard
- Valuation Summary Workbook
- Valuation Flags CSV

---

# ✨ Engineering Highlights

- Modular architecture following separation of concerns
- SQLite-backed financial analytics pipeline
- Config-driven stock screener engine
- Peer percentile ranking system
- Automated Excel report generation
- Radar chart visualization
- Automated testing using Pytest
- Reusable analytics modules
- Analyst-friendly YAML configuration
- Interactive multi-page Streamlit dashboard
- Plotly-based financial visualizations
- Cached SQLite data layer
- Capital allocation analysis
- Annual report integration
- Valuation engine with sector-relative analysis

---

# 🔮 Future Enhancements

- Valuation Models (DCF & Relative Valuation)
- Power BI Integration
- Portfolio Optimizer
- Technical Indicator Engine
- Automated Market Data APIs
- Docker Deployment
- CI/CD Pipeline
- Cloud Deployment

---

# 📌 Project Status

✅ Sprint 1 – Data Pipeline & ETL

✅ Sprint 2 – Financial KPI Engine

✅ Sprint 3 – Screening & Peer Analytics

✅ Sprint 4 – Interactive Dashboard & Valuation Module

### Current Status

✔ 8-screen Streamlit dashboard completed

✔ Financial analytics pipeline completed

✔ Valuation module completed

✔ Interactive stock screener completed

✔ Peer comparison and sector analytics completed

✔ Annual reports explorer completed

✔ Documentation updated

✔ Ready for internship demonstration and evaluation

---

# 📸 Dashboard Screens

The Streamlit dashboard consists of:

## 🏠 Home Dashboard
Displays overall market KPIs, sector distribution, and top quality companies.

## 🏢 Company Profile
Shows company information, financial KPIs, historical charts, and pros & cons.

## 🔍 Stock Screener
Interactive screener with configurable financial filters and CSV export.

## 🤝 Peer Comparison
Compare companies within peer groups using radar charts and KPI tables.

## 📈 Trend Analysis
Visualize historical financial metrics with multi-metric comparison.

## 🏭 Sector Analysis
Analyze companies within sectors using bubble charts and sector medians.

## 💰 Capital Allocation Map
Treemap visualization of companies grouped by capital allocation strategy.

## 📄 Annual Reports
Access historical annual report links directly from the dashboard.

---

# ⚡ Performance

- Streamlit caching implemented using `@st.cache_data`
- SQLite backend for fast local querying
- Dashboard tested across all available dashboard screens
- Charts render responsively without page overflow

---

# 📋 Sprint 4 Retrospective

### UX Decisions

- Used a multi-page Streamlit dashboard for intuitive navigation.
- Added KPI cards for quick financial insights.
- Used Plotly interactive charts for better visualization.
- Implemented sidebar filters for dynamic analysis.
- Added CSV download functionality for screener results.

### Data Edge Cases

- Missing financial values are displayed as **N/A** instead of causing errors.
- Companies with limited historical data still render available charts.
- Annual reports display **Report unavailable** when no valid URL exists.
- Pros & Cons gracefully handle unavailable records.

### Performance

- Database queries are cached using `@st.cache_data(ttl=600)`.
- Dashboard loads efficiently using SQLite backend.
- Company Profile page loads within the expected performance range on local execution.

### Key Deliverables

- 8-screen Streamlit dashboard
- Financial KPI engine
- Interactive stock screener
- Peer comparison dashboard
- Valuation module
- Automated valuation reports

---

# 📋 Sprint 5 Retrospective

### 📄 Automated Company Tear Sheets

* Generated automated financial tear sheets for the Nifty 100 company universe.
* Tear sheets include company information, key financial KPIs, revenue and profit trends, ROE vs ROCE, balance-sheet composition, cash-flow analysis, and pros & cons.
* Companies with fewer than 3 years of available financial data were skipped and logged in `output/skipped_tearsheets.csv`.
* Final output contains **91 company tear-sheet PDFs** because JIOFIN had only 2 years of available data.
* Tear sheets were checked for minimum file size and all generated PDFs were above the 30 KB threshold.

### 🏭 Sector Reports

* Added automated sector-level report generation using the sector mapping in `data/raw/supporting_datasets/sectors.xlsx`.
* The sector mapping covers **92 companies across 10 broad sectors**.
* Generated 10 sector PDF reports under `reports/sector/`.
* Sector reports summarize company-level financial metrics and provide sector-level analysis.

### 💰 Cash-Flow Intelligence

* Added cash-flow quality analysis using CFO/PAT relationships.
* Added CapEx intensity classification.
* Added free-cash-flow conversion metrics.
* Added distress flags based on negative operating cash flow combined with positive financing cash flow.
* Added deleveraging detection using changes in borrowings and financing cash flow.
* Generated `output/cashflow_intelligence.xlsx` containing **92 companies**.
* Generated `output/distress_alerts.csv` containing **13 distress alerts**.

### 📊 Portfolio Summary

* Generated `reports/portfolio/portfolio_summary.pdf`.
* The portfolio summary contains **91 pages**, with one page per available company.
* Companies are presented alphabetically by ticker.
* The report provides a consolidated portfolio-level view of company financial KPIs.

### 🧹 Data & Edge Cases

* Preserved the existing 92-company universe while allowing report generation to skip companies without sufficient historical data.
* JIOFIN was explicitly logged as having fewer than 3 years of data.
* ATGL and SBIN contained missing financial statement components; the reporting pipeline handled these cases without stopping the complete batch.
* Sector classification was sourced from the existing `sectors.xlsx` supporting dataset rather than being added as a new database column.

### 📦 Sprint 5 Deliverables

* `output/pros_cons_generated.csv` — pros and cons for all 92 companies.
* `output/analysis_parsed.csv` — structured CAGR data from analysis data.
* `output/cashflow_intelligence.xlsx` — CFO quality, CapEx intensity, FCF conversion, distress and deleveraging indicators for 92 companies.
* `output/distress_alerts.csv` — companies identified with distress signals.
* `reports/tearsheets/` — 91 generated company tear-sheet PDFs, with JIOFIN skipped due to insufficient history.
* `reports/sector/` — 10 sector report PDFs.
* `reports/portfolio/portfolio_summary.pdf` — 91-page portfolio summary.
* `src/reports/tearsheet.py` — automated company tear-sheet generation.
* `src/reports/sector_report.py` — automated sector report generation.
* `src/reports/portfolio_summary.py` — automated portfolio summary generation.

### 📈 Sprint 5 Outcome

* Automated company-level reporting completed.
* Sector-level reporting completed.
* Portfolio summary generation completed.
* Cash-flow intelligence extended to all 92 companies.
* Pros and cons generated for all 92 companies, with one pro and one con for each company.
* Reporting pipeline now handles missing and limited financial data without failing the complete batch.

### 🔍 Review Status

* Company tear-sheet generation verified.
* Sector report generation verified across all 10 mapped sectors.
* Portfolio summary PDF verified at 91 pages.
* Cash-flow intelligence verified at 92 company rows.
* Pros & Cons output verified at 92 unique companies with both `pro` and `con` entries.
* Sprint 5 reporting and analytics deliverables completed.

---

# 📄 Disclaimer

This project was developed as part of a financial analytics workflow for educational and engineering purposes. It should not be interpreted as investment advice.