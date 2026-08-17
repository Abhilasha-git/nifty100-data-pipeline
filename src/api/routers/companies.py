import sqlite3

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)

DB_PATH = "db/nifty100.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("")
def list_companies(
    search: str | None = Query(default=None),
):
    conn = get_db()

    try:
        query = """
            SELECT
                id,
                company_name,
                roe_percentage AS roe_pct,
                roce_percentage AS roce_pct
            FROM companies
            WHERE 1 = 1
        """

        parameters = []

        if search:
            query += """
                AND (
                    id LIKE ?
                    OR company_name LIKE ?
                )
            """

            search_pattern = f"%{search}%"
            parameters.extend([
                search_pattern,
                search_pattern,
            ])

        query += """
            ORDER BY company_name
        """

        rows = conn.execute(
            query,
            parameters,
        ).fetchall()

        return {
            "count": len(rows),
            "companies": [dict(row) for row in rows],
        }

    finally:
        conn.close()


@router.get("/{company_id}/pl")
def get_company_pl(
    company_id: str,
    from_year: int | None = Query(default=None),
    to_year: int | None = Query(default=None),
):
    conn = get_db()

    try:
        query = """
            SELECT
                year,
                sales,
                expenses,
                operating_profit,
                opm_percentage,
                other_income,
                interest,
                depreciation,
                profit_before_tax,
                tax_percentage,
                net_profit,
                eps,
                dividend_payout
            FROM profitandloss
            WHERE company_id = ?
        """

        parameters = [company_id.upper()]

        if from_year is not None:
            query += " AND year >= ?"
            parameters.append(from_year)

        if to_year is not None:
            query += " AND year <= ?"
            parameters.append(to_year)

        query += " ORDER BY year"

        rows = conn.execute(query, parameters).fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="P&L data not found for company",
            )

        return {
            "company_id": company_id.upper(),
            "history": [dict(row) for row in rows],
        }

    finally:
        conn.close()



@router.get("/{company_id}/bs")
def get_company_bs(
    company_id: str,
    from_year: int | None = Query(default=None),
    to_year: int | None = Query(default=None),
):
    conn = get_db()

    try:
        query = """
            SELECT
                year,
                equity_capital,
                reserves,
                borrowings,
                other_liabilities,
                total_liabilities,
                fixed_assets,
                cwip,
                investments,
                other_asset,
                total_assets
            FROM balancesheet
            WHERE company_id = ?
        """

        parameters = [company_id.upper()]

        if from_year is not None:
            query += " AND year >= ?"
            parameters.append(from_year)

        if to_year is not None:
            query += " AND year <= ?"
            parameters.append(to_year)

        query += " ORDER BY year"

        rows = conn.execute(query, parameters).fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="Balance sheet data not found for company",
            )

        return {
            "company_id": company_id.upper(),
            "history": [dict(row) for row in rows],
        }

    finally:
        conn.close()



@router.get("/{company_id}/cashflow")
def get_company_cashflow(
    company_id: str,
    from_year: int | None = Query(default=None),
    to_year: int | None = Query(default=None),
):
    conn = get_db()

    try:
        query = """
            SELECT
                year,
                operating_activity,
                investing_activity,
                financing_activity,
                net_cash_flow
            FROM cashflow
            WHERE company_id = ?
        """

        parameters = [company_id.upper()]

        if from_year is not None:
            query += " AND year >= ?"
            parameters.append(from_year)

        if to_year is not None:
            query += " AND year <= ?"
            parameters.append(to_year)

        query += " ORDER BY year"

        rows = conn.execute(query, parameters).fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="Cash flow data not found for company",
            )

        return {
            "company_id": company_id.upper(),
            "history": [dict(row) for row in rows],
        }

    finally:
        conn.close()




@router.get("/{company_id}/ratios")
def get_company_ratios(
    company_id: str,
    from_year: int | None = Query(default=None),
    to_year: int | None = Query(default=None),
):
    conn = get_db()

    try:
        query = """
            SELECT
                year,
                net_profit_margin_pct,
                operating_profit_margin_pct,
                return_on_equity_pct,
                return_on_capital_employed_pct,
                return_on_assets_pct,
                debt_to_equity,
                interest_coverage,
                asset_turnover,
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
        """

        parameters = [company_id.upper()]

        if from_year is not None:
            query += " AND year >= ?"
            parameters.append(from_year)

        if to_year is not None:
            query += " AND year <= ?"
            parameters.append(to_year)

        query += " ORDER BY year"

        rows = conn.execute(
            query,
            parameters,
        ).fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="Financial ratio data not found for company",
            )

        return {
            "company_id": company_id.upper(),
            "history": [dict(row) for row in rows],
        }

    finally:
        conn.close()


@router.get("/{company_id}")
def get_company(company_id: str):
    conn = get_db()

    try:
        row = conn.execute(
            """
            SELECT *
            FROM companies
            WHERE id = ?
            """,
            (company_id.upper(),),
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Company not found",
            )

        return dict(row)

    finally:
        conn.close()
