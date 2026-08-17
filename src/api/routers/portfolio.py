import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)

DB_PATH = "db/nifty100.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("")
def get_portfolio():
    conn = get_db()

    try:
        return {
            "message": "Portfolio endpoint ready",
            "holdings": [],
        }

    finally:
        conn.close()


@router.get("/{company_id}")
def get_portfolio_company(company_id: str):
    conn = get_db()

    try:
        row = conn.execute(
            """
            SELECT
                id,
                company_name,
                book_value,
                roce_percentage,
                roe_percentage
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

        return {
            "company_id": row["id"],
            "company_name": row["company_name"],
            "book_value": row["book_value"],
            "roe_percentage": row["roe_percentage"],
            "roce_percentage": row["roce_percentage"],
        }

    finally:
        conn.close()