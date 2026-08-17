from fastapi import APIRouter, HTTPException

from src.api.database import get_db_connection

router = APIRouter(
    prefix="/valuation",
    tags=["Valuation"],
)


@router.get("/{company_id}")
def get_valuation(company_id: str):
    connection = get_db_connection()

    try:
        company = connection.execute(
            """
            SELECT
                id,
                company_name,
                face_value,
                book_value,
                roce_percentage,
                roe_percentage
            FROM companies
            WHERE id = ?
            """,
            (company_id,),
        ).fetchone()

        if company is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{company_id}' not found",
            )

        ratios = connection.execute(
            """
            SELECT
                year,
                net_profit_margin_pct,
                operating_profit_margin_pct,
                debt_to_equity,
                interest_coverage,
                free_cash_flow_cr,
                capex_intensity_pct,
                fcf_conversion_rate_pct,
                cfo_pat_ratio,
                cfo_quality_label,
                capital_allocation_pattern,
                revenue_cagr_5yr,
                pat_cagr_5yr,
                eps_cagr_5yr
            FROM financial_ratios
            WHERE company_id = ?
            ORDER BY year DESC
            LIMIT 1
            """,
            (company_id,),
        ).fetchone()

        pnl = connection.execute(
            """
            SELECT
                year,
                sales,
                operating_profit,
                net_profit,
                eps,
                dividend_payout
            FROM profitandloss
            WHERE company_id = ?
            ORDER BY year DESC
            LIMIT 1
            """,
            (company_id,),
        ).fetchone()

        result = {
            "company_id": company["id"],
            "company_name": company["company_name"],
            "year": ratios["year"] if ratios else (
                pnl["year"] if pnl else None
            ),
            "face_value": company["face_value"],
            "book_value": company["book_value"],
            "roe_percentage": company["roe_percentage"],
            "roce_percentage": company["roce_percentage"],
            "sales": pnl["sales"] if pnl else None,
            "operating_profit": pnl["operating_profit"] if pnl else None,
            "net_profit": pnl["net_profit"] if pnl else None,
            "eps": pnl["eps"] if pnl else None,
            "dividend_payout": pnl["dividend_payout"] if pnl else None,
            "net_profit_margin_pct": (
                ratios["net_profit_margin_pct"] if ratios else None
            ),
            "operating_profit_margin_pct": (
                ratios["operating_profit_margin_pct"] if ratios else None
            ),
            "debt_to_equity": (
                ratios["debt_to_equity"] if ratios else None
            ),
            "interest_coverage": (
                ratios["interest_coverage"] if ratios else None
            ),
            "free_cash_flow_cr": (
                ratios["free_cash_flow_cr"] if ratios else None
            ),
            "revenue_cagr_5yr": (
                ratios["revenue_cagr_5yr"] if ratios else None
            ),
            "pat_cagr_5yr": (
                ratios["pat_cagr_5yr"] if ratios else None
            ),
            "eps_cagr_5yr": (
                ratios["eps_cagr_5yr"] if ratios else None
            ),
            "cfo_quality_label": (
                ratios["cfo_quality_label"] if ratios else None
            ),
            "capital_allocation_pattern": (
                ratios["capital_allocation_pattern"] if ratios else None
            ),
        }

        return result

    finally:
        connection.close()
