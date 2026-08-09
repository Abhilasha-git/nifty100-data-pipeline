from pathlib import Path
import sqlite3

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


DB = "db/nifty100.db"

OUTPUT_DIR = Path("reports/portfolio")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PDF = OUTPUT_DIR / "portfolio_summary.pdf"

SECTOR_FILE = "data/raw/supporting_datasets/sectors.xlsx"


styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "PortfolioTitle",
    parent=styles["Title"],
    fontSize=20,
    leading=24,
    textColor=colors.HexColor("#0B1F3A"),
    alignment=TA_CENTER,
    spaceAfter=10,
)

subtitle_style = ParagraphStyle(
    "PortfolioSubtitle",
    parent=styles["Normal"],
    fontSize=10,
    leading=13,
    textColor=colors.HexColor("#555555"),
    alignment=TA_CENTER,
)

kpi_style = ParagraphStyle(
    "KPI",
    parent=styles["Normal"],
    fontSize=10,
    leading=13,
    alignment=TA_CENTER,
)

small_style = ParagraphStyle(
    "Small",
    parent=styles["Normal"],
    fontSize=8,
    leading=10,
)


def load_data():
    conn = sqlite3.connect(DB)

    companies = pd.read_sql(
        """
        SELECT
            id AS ticker,
            company_name
        FROM companies
        """,
        conn,
    )

    ratios = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        WHERE year IS NOT NULL
        ORDER BY company_id, year
        """,
        conn,
    )

    conn.close()

    sectors = pd.read_excel(SECTOR_FILE)

    sectors = sectors[
        ["company_id", "broad_sector"]
    ].drop_duplicates()

    companies = companies.merge(
        sectors,
        left_on="ticker",
        right_on="company_id",
        how="left",
    )

    companies = companies.drop(columns=["company_id"])

    return companies, ratios


def trend_arrow(current, previous):
    """
    ↑ if improved by more than 2%
    ↓ if declined by more than 2%
    → if within ±2%

    Returns an arrow and the percentage change.
    """

    if pd.isna(current) or pd.isna(previous):
        return "→", None

    if previous == 0:
        return "→", None

    change = (current - previous) / abs(previous) * 100

    if change > 2:
        return "↑", change

    if change < -2:
        return "↓", change

    return "→", change


def format_value(metric, value):
    if pd.isna(value):
        return "N/A"

    if metric in [
        "ROE",
        "ROCE",
        "Revenue CAGR",
        "PAT CAGR",
    ]:
        return f"{float(value):.1f}%"

    if metric == "D/E":
        return f"{float(value):.2f}"

    if metric == "FCF":
        return f"Rs. {float(value):,.0f} Cr"

    return f"{float(value):,.1f}"


def get_kpis(ratios):
    """
    Returns the latest six KPIs plus their previous-year values.
    """

    ratios = ratios.sort_values("year")

    latest = ratios.iloc[-1]

    previous = (
        ratios.iloc[-2]
        if len(ratios) >= 2
        else None
    )

    metrics = [
        ("ROE", "return_on_equity_pct"),
        ("ROCE", "return_on_capital_employed_pct"),
        ("D/E", "debt_to_equity"),
        ("Revenue CAGR", "revenue_cagr_5yr"),
        ("PAT CAGR", "pat_cagr_5yr"),
        ("FCF", "free_cash_flow_cr"),
    ]

    result = []

    for label, column in metrics:

        current = pd.to_numeric(
            latest.get(column),
            errors="coerce",
        )

        previous_value = (
            pd.to_numeric(
                previous.get(column),
                errors="coerce",
            )
            if previous is not None
            else None
        )

        arrow, change = trend_arrow(
            current,
            previous_value,
        )

        result.append(
            {
                "label": label,
                "value": format_value(
                    label,
                    current,
                ),
                "arrow": arrow,
                "change": change,
            }
        )

    return latest, result


def make_kpi_table(kpis):
    cells = []

    for kpi in kpis:
        arrow_color = {
            "↑": "#16803C",
            "↓": "#C62828",
            "→": "#777777",
        }.get(kpi["arrow"], "#777777")

        cells.append(
            Paragraph(
                f"""
                <b>{kpi['label']}</b><br/>
                <font size="15">
                {kpi['value']}
                </font>
                <br/>
                <font color="{arrow_color}" size="14">
                <b>{kpi['arrow']}</b>
                </font>
                """,
                kpi_style,
            )
        )

    table = Table(
        [
            cells[:3],
            cells[3:6],
        ],
        colWidths=[
            2.25 * inch,
            2.25 * inch,
            2.25 * inch,
        ],
        rowHeights=[
            1.0 * inch,
            1.0 * inch,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    colors.HexColor("#CCCCCC"),
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#F5F7FA"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "WORDWRAP",
                    (0, 0),
                    (-1, -1),
                    True,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    return table


def create_portfolio_summary():
    companies, ratios = load_data()

    # Only companies for which a tearsheet exists.
    # This excludes JIOFIN, which has fewer than 3 years.
    existing_tearsheets = {
        p.stem.replace("_tearsheet", "")
        for p in Path("reports/tearsheets").glob(
            "*_tearsheet.pdf"
        )
    }

    companies = companies[
        companies["ticker"].isin(existing_tearsheets)
    ].copy()

    companies = companies.sort_values(
        "ticker"
    )

    print(
        f"Portfolio companies: {len(companies)}"
    )

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
    )

    story = []

    for index, company in companies.iterrows():

        ticker = company["ticker"]
        company_name = company["company_name"]
        sector = company["broad_sector"]

        company_ratios = ratios[
            ratios["company_id"] == ticker
        ].copy()

        company_ratios = company_ratios.dropna(
            subset=["year"]
        )

        if company_ratios.empty:
            continue

        latest, kpis = get_kpis(
            company_ratios
        )

        story.append(
            Paragraph(
                company_name,
                title_style,
            )
        )

        story.append(
            Paragraph(
                f"<b>{ticker}</b>",
                subtitle_style,
            )
        )

        story.append(
            Spacer(
                1,
                0.12 * inch,
            )
        )

        sector_text = (
            str(sector)
            if pd.notna(sector)
            else "Sector unavailable"
        )

        info_table = Table(
            [
                [
                    Paragraph(
                        "<b>Sector</b>",
                        small_style,
                    ),
                    Paragraph(
                        sector_text,
                        small_style,
                    ),
                    Paragraph(
                        "<b>Latest Year</b>",
                        small_style,
                    ),
                    Paragraph(
                        str(int(latest["year"])),
                        small_style,
                    ),
                ]
            ],
            colWidths=[
                1.1 * inch,
                3.0 * inch,
                1.2 * inch,
                1.7 * inch,
            ],
        )

        info_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor(
                            "#EEF2F7"
                        ),
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor(
                            "#D0D5DD"
                        ),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "WORDWRAP",
                        (0, 0),
                        (-1, -1),
                        True,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        story.append(info_table)

        story.append(
            Spacer(
                1,
                0.25 * inch,
            )
        )

        story.append(
            Paragraph(
                "<b>Key Performance Indicators</b>",
                styles["Heading2"],
            )
        )

        story.append(
            Spacer(
                1,
                0.08 * inch,
            )
        )

        story.append(
            make_kpi_table(kpis)
        )

        story.append(
            Spacer(
                1,
                0.3 * inch,
            )
        )

        story.append(
            Paragraph(
                """
                <b>Trend legend:</b>
                ↑ improved &nbsp;&nbsp;
                ↓ declined &nbsp;&nbsp;
                → flat within 2%
                """,
                small_style,
            )
        )

        # Every company gets exactly one page.
        if index != companies.index[-1]:
            story.append(PageBreak())

    doc.build(story)

    print(
        f"Portfolio summary created: {OUTPUT_PDF}"
    )


if __name__ == "__main__":
    create_portfolio_summary()