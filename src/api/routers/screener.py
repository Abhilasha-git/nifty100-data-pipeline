from fastapi import APIRouter, Query

from src.api.database import get_db_connection

router = APIRouter(
    prefix="/screener",
    tags=["Screener"],
)


@router.get("")
def screen_companies(
    min_roe: float | None = Query(
        default=None,
        description="Minimum return on equity (%)",
    ),
    max_debt_to_equity: float | None = Query(
        default=None,
        description="Maximum debt-to-equity ratio",
    ),
    min_revenue_cagr: float | None = Query(
        default=None,
        description="Minimum 5-year revenue CAGR (%)",
    ),
    min_opm: float | None = Query(
        default=None,
        description="Minimum operating profit margin (%)",
    ),
):
    connection = get_db_connection()

    try:
        query = """
            SELECT
                fr.company_id,
                c.company_name,
                fr.year,
                fr.return_on_equity_pct,
                fr.debt_to_equity,
                CAST(fr.revenue_cagr_5yr AS REAL)
                    AS revenue_cagr_5yr,
                fr.operating_profit_margin_pct
            FROM financial_ratios fr
            LEFT JOIN companies c
                ON c.id = fr.company_id
            INNER JOIN (
                SELECT
                    company_id,
                    MAX(year) AS latest_year
                FROM financial_ratios
                GROUP BY company_id
            ) latest
                ON latest.company_id = fr.company_id
                AND latest.latest_year = fr.year
            WHERE 1 = 1
        """

        conditions = []
        parameters = []

        if min_roe is not None:
            conditions.append(
                "fr.return_on_equity_pct >= ?"
            )
            parameters.append(min_roe)

        if max_debt_to_equity is not None:
            conditions.append(
                "fr.debt_to_equity <= ?"
            )
            parameters.append(max_debt_to_equity)

        if min_revenue_cagr is not None:
            conditions.append(
                "CAST(fr.revenue_cagr_5yr AS REAL) >= ?"
            )
            parameters.append(min_revenue_cagr)

        if min_opm is not None:
            conditions.append(
                "fr.operating_profit_margin_pct >= ?"
            )
            parameters.append(min_opm)

        if conditions:
            query += " AND " + " AND ".join(conditions)

        query += """
            ORDER BY fr.return_on_equity_pct DESC
        """

        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

        return {
            "count": len(rows),
            "results": [dict(row) for row in rows],
        }

    finally:
        connection.close()
