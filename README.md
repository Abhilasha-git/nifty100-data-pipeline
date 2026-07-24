# 📈 Nifty100 Data Pipeline

A production-style financial analytics pipeline built in Python for analyzing Nifty 100 companies. The project automates financial KPI computation, peer-group benchmarking, composite quality scoring, configurable stock screening, and Excel report generation.

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
│   └── peer_comparison.xlsx
│
├── reports/
│   └── radar_charts/
│       ├── ABB_radar.png
│       ├── TCS_radar.png
│       └── ...
│
├── scripts/
│
├── src/
│   │
│   ├── analytics/
│   │   ├── cagr.py
│   │   ├── cashflow_kpis.py
│   │   ├── peer.py
│   │   ├── peer_summary.py
│   │   └── ratios.py
│   │
│   ├── config/
│   │   └── screener_config.yaml
│   │
│   ├── etl/
│   │   ├── loader.py
│   │   ├── normaliser.py
│   │   └── validator.py
│   │
│   ├── reports/
│   │   ├── peer_report.py
│   │   └── radar.py
│   │
│   ├── scoring/
│   │   └── score_engine.py
│   │
│   ├── screener/
│   │   ├── engine.py
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
│
├── screener_output.xlsx
└── peer_comparison.xlsx

reports/
└── radar_charts/
```

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

---

# 🔮 Future Enhancements

- Streamlit Dashboard
- Power BI Integration
- Portfolio Optimizer
- Valuation Models (DCF & Relative Valuation)
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

---

# 📄 Disclaimer

This project was developed as part of a financial analytics workflow for educational and engineering purposes. It should not be interpreted as investment advice.