from pathlib import Path
import sqlite3

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
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

SECTOR_REPORTS = Path("reports/sector")
SECTOR_REPORTS.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()


def load_sector_data():
    conn = sqlite3.connect(DB)

    df = pd.read_sql(
        """
        SELECT
            c.id AS ticker,
            c.company_name,
            r.year,
            r.return_on_equity_pct,
            r.return_on_capital_employed_pct,
            r.debt_to_equity,
            r.revenue_cagr_5yr,
            r.pat_cagr_5yr,
            r.free_cash_flow_cr,
            r.net_profit_margin_pct,
            r.operating_profit_margin_pct
        FROM companies c
        JOIN financial_ratios r
            ON c.id = r.company_id
        WHERE r.year IS NOT NULL
        ORDER BY c.id, r.year
        """,
        conn,
    )

    conn.close()

    # Load sector mapping from supporting dataset
    sectors = pd.read_excel(
        "data/raw/supporting_datasets/sectors.xlsx"
    )

    # Keep only the columns required for the sector report
    sectors = sectors[
        ["company_id", "broad_sector", "sub_sector"]
    ].copy()

    # Rename company_id to ticker so it matches the database data
    sectors = sectors.rename(
        columns={"company_id": "ticker"}
    )

    # Merge sector information
    df = df.merge(
        sectors,
        on="ticker",
        how="left",
    )

    # Use broad_sector as the report sector
    df["sector"] = df["broad_sector"]

    # Remove rows where sector could not be mapped
    df = df.dropna(subset=["sector"])

    return df


def latest_company_rows(df):
    """
    Keep the latest available financial-ratio row for each company.
    """
    df = df.dropna(subset=["year"]).copy()

    if df.empty:
        return df

    return (
        df.sort_values("year")
        .groupby("ticker", as_index=False)
        .tail(1)
        .reset_index(drop=True)
    )


def fmt(value, suffix="", decimals=1):
    """
    Safely format numeric values.
    """
    value = pd.to_numeric(value, errors="coerce")

    if pd.isna(value):
        return "N/A"

    return f"{value:.{decimals}f}{suffix}"


def create_sector_report(sector, sector_df):
    """
    Create one PDF for one sector.
    """

    sector_df = latest_company_rows(sector_df)

    if sector_df.empty:
        print(f"Skipping {sector}: no data")
        return

    safe_sector = (
        str(sector)
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )

    pdf_path = SECTOR_REPORTS / f"{safe_sector}_report.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    story = []

    # ---------------------------------------------------------
    # TITLE
    # ---------------------------------------------------------

    title = Paragraph(
        f"""
        <font color="#0B1F3A" size="20">
        <b>{sector}</b>
        </font>
        """,
        styles["Title"],
    )

    story.append(title)
    story.append(Spacer(1, 0.15 * inch))

    story.append(
        Paragraph(
            f"Companies covered: {len(sector_df)}",
            styles["BodyText"],
        )
    )

    story.append(Spacer(1, 0.25 * inch))

    # ---------------------------------------------------------
    # MEDIAN KPI SUMMARY
    # ---------------------------------------------------------

    median_columns = [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "free_cash_flow_cr",
    ]

    median_labels = [
        "Median ROE",
        "Median ROCE",
        "Median D/E",
        "Median Revenue CAGR",
        "Median PAT CAGR",
        "Median FCF",
    ]

    median_values = []

    for column in median_columns:
        median_values.append(
            pd.to_numeric(
                sector_df[column],
                errors="coerce",
            ).median()
        )

    summary_data = [
        [
            Paragraph(f"<b>{label}</b>", styles["BodyText"])
            for label in median_labels
        ],
        [
            Paragraph(
                fmt(value, "%" if i != 2 and i != 5 else "", 1),
                styles["BodyText"],
            )
            for i, value in enumerate(median_values)
        ],
    ]

    # FCF should display Cr.
    summary_data[1][5] = Paragraph(
        fmt(median_values[5], " Cr", 0),
        styles["BodyText"],
    )

    summary_table = Table(
        summary_data,
        colWidths=[1.2 * inch] * 6,
    )

    summary_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.7, colors.grey),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#DCE6F1"),
                ),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("WORDWRAP", (0, 0), (-1, -1), True),
            ]
        )
    )

    story.append(summary_table)

    story.append(Spacer(1, 0.3 * inch))

    # ---------------------------------------------------------
    # COMPANY TABLE
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "<b>Companies in Sector</b>",
            styles["Heading2"],
        )
    )

    story.append(Spacer(1, 0.1 * inch))

    headers = [
        "Ticker",
        "Company",
        "ROE",
        "ROCE",
        "D/E",
        "Revenue CAGR",
        "PAT CAGR",
        "FCF",
    ]

    table_data = [
        [
            Paragraph(f"<b>{header}</b>", styles["BodyText"])
            for header in headers
        ]
    ]

    for _, row in sector_df.iterrows():
        table_data.append(
            [
                Paragraph(str(row["ticker"]), styles["BodyText"]),
                Paragraph(str(row["company_name"]), styles["BodyText"]),
                Paragraph(
                    fmt(row["return_on_equity_pct"], "%", 1),
                    styles["BodyText"],
                ),
                Paragraph(
                    fmt(
                        row["return_on_capital_employed_pct"],
                        "%",
                        1,
                    ),
                    styles["BodyText"],
                ),
                Paragraph(
                    fmt(row["debt_to_equity"], "", 2),
                    styles["BodyText"],
                ),
                Paragraph(
                    fmt(row["revenue_cagr_5yr"], "%", 1),
                    styles["BodyText"],
                ),
                Paragraph(
                    fmt(row["pat_cagr_5yr"], "%", 1),
                    styles["BodyText"],
                ),
                Paragraph(
                    fmt(row["free_cash_flow_cr"], " Cr", 0),
                    styles["BodyText"],
                ),
            ]
        )

    company_table = Table(
        table_data,
        colWidths=[
            0.75 * inch,
            1.55 * inch,
            0.65 * inch,
            0.65 * inch,
            0.55 * inch,
            0.85 * inch,
            0.75 * inch,
            0.85 * inch,
        ],
        repeatRows=1,
    )

    company_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#0B1F3A"),
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (2, 1), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("WORDWRAP", (0, 0), (-1, -1), True),
            ]
        )
    )

    story.append(company_table)

    doc.build(story)

    print(pdf_path)


def main():
    df = load_sector_data()

    if df.empty:
        print("No sector data found.")
        return

    sectors = sorted(
        df["sector"]
        .dropna()
        .astype(str)
        .unique()
    )

    print(f"Found {len(sectors)} sectors")

    for sector in sectors:
        sector_df = df[df["sector"].astype(str) == sector]
        create_sector_report(sector, sector_df)

    print("Sector report generation complete.")


if __name__ == "__main__":
    main()