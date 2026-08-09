from pathlib import Path
import sqlite3

import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib import colors
#from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)

DB = "db/nifty100.db"

REPORTS = Path("reports/tearsheets")
REPORTS.mkdir(parents=True, exist_ok=True)

OUTPUT = Path("output")

styles = getSampleStyleSheet()

def load_company_data(ticker):
    conn = sqlite3.connect(DB)
    
    company = pd.read_sql(
    """
    SELECT *
    FROM companies
    WHERE id=?
    """,
    conn,
    params=[ticker],
    )
    
    ratios = pd.read_sql(
    """
    SELECT *
    FROM financial_ratios
    WHERE company_id=?
    ORDER BY YEAR
    """,
    conn,
    params=[ticker],
    )
    
    ratios = ratios.dropna(subset=["year"])
    
    pl = pd.read_sql(
    """
    SELECT *
    FROM profitandloss
    WHERE company_id=?
    ORDER BY YEAR
    """,
    conn,
    params=[ticker],
    )
    
    pl = pl.dropna(subset=["year"])
    
    bs = pd.read_sql(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id=?
        ORDER BY YEAR
        """,
        conn,
        params=[ticker],
    )
    bs = bs.dropna(subset=["year"])
    
    cf = pd.read_sql(
        """
        SELECT *
        FROM cashflow
        WHERE company_id=?
        ORDER BY year
        """,
        conn,
        params=[ticker],
    )
    
    cf = cf.dropna(subset=["year"])
    
    conn.close()
    return company, ratios, pl, bs, cf

def load_pros_cons(ticker):

    path = OUTPUT / "pros_cons_generated.csv"

    if not path.exists():
        return [], []

    df = pd.read_csv(path)

    df = df[df.company_id == ticker]

    pros = df[df.type == "pro"]["text"].tolist()

    cons = df[df.type == "con"]["text"].tolist()

    return pros, cons

def latest_row(df):

    if df.empty:
        return None

    df = df.dropna(subset=["year"])

    if df.empty:
        return None

    return df.sort_values("year").iloc[-1]

def revenue_chart(pl, ticker):
    plt.figure(figsize=(4, 2.5))

    plt.bar(
        pl["year"],
        pl["sales"],
    )

    plt.title("Revenue")
    plt.tight_layout()

    path = REPORTS / f"{ticker}_revenue.png"
    plt.savefig(path, dpi=150)
    plt.close()

    return str(path)

def profit_chart(pl, ticker):
    plt.figure(figsize=(4, 2.5))

    plt.bar(
        pl["year"],
        pl["net_profit"],
    )

    plt.title("Net Profit")
    plt.tight_layout()

    path = REPORTS / f"{ticker}_profit.png"
    plt.savefig(path, dpi=150)
    plt.close()

    return str(path)

def roe_roce_chart(ratios, ticker):
    plt.figure(figsize=(5, 3))

    plt.plot(
        ratios["year"],
        ratios["return_on_equity_pct"],
        marker="o",
        label="ROE",
    )

    plt.plot(
        ratios["year"],
        ratios["return_on_capital_employed_pct"],
        marker="s",
        label="ROCE",
    )

    plt.legend()

    plt.title("ROE vs ROCE")

    plt.tight_layout()

    path = REPORTS / f"{ticker}_roe_roce.png"

    plt.savefig(path, dpi=150)

    plt.close()

    return str(path)

def balance_sheet_chart(bs, ticker):
    if bs.empty:
        plt.figure(figsize=(6, 3))
        plt.text(
            0.5,
            0.5,
            "Balance Sheet data unavailable",
            ha="center",
            va="center",
        )
        plt.axis("off")
        
        path = REPORTS / f"{ticker}_bs.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        
        return str(path)

    equity = bs["equity_capital"].fillna(0) + bs["reserves"].fillna(0)
    borrowings = bs["borrowings"].fillna(0)
    other = bs["other_liabilities"].fillna(0)

    plt.bar(bs["year"], equity, label="Equity")
    plt.bar(
        bs["year"],
        borrowings,
        bottom=equity,
        label="Borrowings",
    )
    plt.bar(
        bs["year"],
        other,
        bottom=equity + borrowings,
        label="Other Liabilities",
    )

    plt.title("Balance Sheet Composition")
    plt.legend()
    plt.tight_layout()

    path = REPORTS / f"{ticker}_bs.png"
    plt.savefig(path, dpi=150)
    plt.close()

    return str(path)


def cashflow_waterfall(cf, ticker):
    latest = latest_row(cf)

    if latest is None:
        plt.figure(figsize=(6, 3))
        plt.text(
            0.5,
            0.5,
            "Cash Flow data unavailable",
            ha="center",
            va="center",
        )
        plt.axis("off")

        path = REPORTS / f"{ticker}_cf.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()

        return str(path)

    labels = ["CFO", "CFI", "CFF", "Net Cash Flow"]

    cfo = float(latest["operating_activity"] or 0)
    cfi = float(latest["investing_activity"] or 0)
    cff = float(latest["financing_activity"] or 0)

    net_cash_flow = cfo + cfi + cff

    values = [cfo, cfi, cff, net_cash_flow]

    plt.figure(figsize=(6, 3))

    bar_colors = [
        "green" if value >= 0 else "red"
        for value in values
    ]

    plt.bar(labels, values, color=bar_colors)

    plt.axhline(0, linewidth=0.8)
    plt.title(f"Cash Flow — {int(latest['year'])}")
    plt.tight_layout()

    path = REPORTS / f"{ticker}_cf.png"
    plt.savefig(path, dpi=150)
    plt.close()

    return str(path)

def create_tearsheet(ticker):
    
    
    company, ratios, pl, bs, cf = load_company_data(ticker)

    if company.empty:
        print(f"{ticker} not found")
        return

    company = company.iloc[0]

# Remove invalid year rows
    ratios = ratios.dropna(subset=["year"]).copy()
    pl = pl.dropna(subset=["year"]).copy()
    bs = bs.dropna(subset=["year"]).copy()
    cf = cf.dropna(subset=["year"]).copy()

# Make sure there is enough data for the charts
    if len(pl) < 3:
        print(f"{ticker}: insufficient P&L data")
        return

    if len(ratios) < 3:
        print(f"{ticker}: insufficient ratio data")
        return

    if bs.empty:
        print(f"{ticker}: no balance-sheet data — using placeholder")
    
    if cf.empty:
        print(f"{ticker}: no cash-flow data — using placeholder")

    latest_ratio = latest_row(ratios)

    if latest_ratio is None:
        print(f"{ticker}: no ratio data")
        return

    latest_pl = latest_row(pl)

    pros, cons = load_pros_cons(ticker)

    revenue_img = revenue_chart(pl, ticker)
    profit_img = profit_chart(pl, ticker)
    roe_img = roe_roce_chart(ratios, ticker)

    bs_img = balance_sheet_chart(bs, ticker)
    cf_img = cashflow_waterfall(cf, ticker)
    
    pdf_path = str(REPORTS / f"{ticker}_tearsheet.pdf")
    
    doc = SimpleDocTemplate(pdf_path)
    
    #styles = getSampleStyleSheet()
    
    story = []
    
    header = Table(
        [[
            Paragraph(
                f"""
                <font color="white" size="20">
                <b>{company.company_name}</b>
                </font>
                <br/>
                <font color="white" size="12">
                {ticker}
                </font>
                """,
                styles["BodyText"],
            )
        ]],
        colWidths=[7.0 * inch],
    )

    header.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0B1F3A")),
            ("LEFTPADDING", (0, 0), (-1, -1), 15),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("WORDWRAP", (0, 0), (-1, -1), True),
        ])
    )

    story.append(header)
    story.append(Spacer(1, 0.2 * inch))
    
    
    revenue_cagr = pd.to_numeric(
        latest_ratio.revenue_cagr_5yr,
        errors="coerce",
    )

    pat_cagr = pd.to_numeric(
        latest_ratio.pat_cagr_5yr,
        errors="coerce",
    )

    roe = (
        f"{latest_ratio.return_on_equity_pct:.1f}%"
        if pd.notna(latest_ratio.return_on_equity_pct)
        else "N/A"
    )

    roce = (
        f"{latest_ratio.return_on_capital_employed_pct:.1f}%"
        if pd.notna(latest_ratio.return_on_capital_employed_pct)
        else "N/A"
    )

    de = (
        f"{latest_ratio.debt_to_equity:.2f}"
        if pd.notna(latest_ratio.debt_to_equity)
        else "N/A"
    )

    rev = (
        f"{revenue_cagr:.1f}%"
        if pd.notna(revenue_cagr)
        else "N/A"
    )

    pat = (
        f"{pat_cagr:.1f}%"
        if pd.notna(pat_cagr)
        else "N/A"
    )

    fcf = (
        f"Rs. {latest_ratio.free_cash_flow_cr:,.0f} Cr"
        if pd.notna(latest_ratio.free_cash_flow_cr)
        else "N/A"
    )
 
    kpis = [
        [
            Paragraph(f"<b>ROE</b><br/>{roe}", styles["BodyText"]),
            Paragraph(f"<b>ROCE</b><br/>{roce}", styles["BodyText"]),
            Paragraph(f"<b>D/E</b><br/>{de}", styles["BodyText"]),
        ],
        [
            Paragraph(
                f"<b>Revenue CAGR</b><br/>{rev}",
                styles["BodyText"],
            ),
            Paragraph(
                f"<b>PAT CAGR</b><br/>{pat}",
                styles["BodyText"],
            ),
            Paragraph(
                f"<b>FCF</b><br/>{fcf}",
                styles["BodyText"],
            ),
        ],
    ]

    kpi_table = Table(
        kpis,
        colWidths=[2.33 * inch] * 3,
        rowHeights=[0.7 * inch, 0.7 * inch],
    )

    kpi_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.8, colors.grey),
            ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("WORDWRAP", (0, 0), (-1, -1), True),
        ])
    )

    story.append(kpi_table)
    story.append(Spacer(1, 0.2 * inch))
    
    
    chart_row = Table(
        [[
            Image(revenue_img, width=3.25 * inch, height=2.2 * inch),
            Image(profit_img, width=3.25 * inch, height=2.2 * inch),
        ]],
        colWidths=[3.5 * inch, 3.5 * inch],
    )

    chart_row.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("WORDWRAP", (0, 0), (-1, -1), True),
        ])
    )

    story.append(chart_row)
    story.append(Spacer(1, 0.1 * inch))

    story.append(
        Image(
            roe_img,
            width=6.5 * inch,
            height=2.5 * inch,
        )
    )
    
    story.append(PageBreak())
    
    story.append(
        Paragraph(
            "<b>Balance Sheet Composition</b>",
            styles["Heading2"],
        )
    )

    story.append(
        Image(
            bs_img,
            width=6.5 * inch,
            height=2.6 * inch,
        )
    )

    story.append(Spacer(1, 0.15 * inch))

    story.append(
        Paragraph(
            "<b>Cash Flow Waterfall</b>",
            styles["Heading2"],
        )
    )

    story.append(
        Image(
            cf_img,
            width=6.5 * inch,
            height=2.6 * inch,
        )
    )

    story.append(Spacer(1, 0.1 * inch))
    
    story.append(
        Paragraph("<b>Pros</b>", styles["Heading2"])
    )

    if pros:
        for p in pros:
            story.append(
                Paragraph(
                    f"<font color='green'>•</font> {p}",
                    styles["BodyText"],
                )
            )
    else:
        story.append(
            Paragraph("No major positives available.", styles["BodyText"])
        )

    story.append(Spacer(1, 0.2 * inch))

    story.append(
        Paragraph("<b>Cons</b>", styles["Heading2"])
    )

    if cons:
        for c in cons:
            story.append(
                Paragraph(
                    f"<font color='red'>•</font> {c}",
                    styles["BodyText"],
                )
            )
    else:
        story.append(
            Paragraph("No major concerns available.", styles["BodyText"])
        )
    
    story.append(Spacer(1,0.3*inch))
    
    
    allocation = str(
        latest_ratio.capital_allocation_pattern
    )

    badge = Table(
        [[
            Paragraph(
                f"<font color='white'><b>{allocation}</b></font>",
                styles["BodyText"],
            )
        ]],
        colWidths=[3.0 * inch],
    )

    badge.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1B5E20")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("WORDWRAP", (0, 0), (-1, -1), True),
        ])
    )

    story.append(
        Paragraph(
            "<b>Capital Allocation</b>",
            styles["Heading2"],
        )
    )

    story.append(badge)
    
    doc.build(story)
    
    print(pdf_path)
    
if __name__ == "__main__":
    conn = sqlite3.connect(DB)

    companies = pd.read_sql(
        """
        SELECT DISTINCT id
        FROM companies
        ORDER BY id
        """,
        conn,
    )

    conn.close()

    skipped = []

    for ticker in companies["id"]:
        try:
            company, ratios, pl, bs, cf = load_company_data(ticker)

            years = set()

            for df in [ratios, pl, bs, cf]:
                if not df.empty and "year" in df.columns:
                    years.update(
                        pd.to_numeric(
                            df["year"], errors="coerce"
                        ).dropna().astype(int)
                    )

            if len(years) < 3:
                print(f"Skipping {ticker}: only {len(years)} years")
                skipped.append(
                    {
                        "ticker": ticker,
                        "years": len(years),
                        "reason": "Fewer than 3 years of data",
                    }
                )
                continue

            create_tearsheet(ticker)

        except Exception as e:
            print(f"ERROR {ticker}: {e}")
            skipped.append(
                {
                    "ticker": ticker,
                    "years": "",
                    "reason": str(e),
                }
            )
        #except Exception as e:
            #print(f"ERROR {ticker}: {e}")
            #raise

    pd.DataFrame(skipped).to_csv(
        OUTPUT / "skipped_tearsheets.csv",
        index=False,
    )

    print("Batch tearsheet generation complete.")
    print(f"Skipped: {len(skipped)}")