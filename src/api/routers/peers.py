import sqlite3

from fastapi import APIRouter, HTTPException, Query

from src.api.database import get_db_connection

router = APIRouter(
    prefix="/peers",
    tags=["Peers"],
)


@router.get("")
def get_peers(
    company_id: str = Query(..., description="Company ID, e.g. TATASTEEL"),
    metric: str | None = Query(None, description="Metric, e.g. ROE"),
    year: float | None = Query(None, description="Financial year"),
):
    connection = get_db_connection()

    try:
        query = """
            SELECT
                company_id,
                peer_group_name,
                metric,
                value,
                percentile_rank,
                year
            FROM peer_percentiles
            WHERE company_id = ?
        """

        params = [company_id.upper()]

        if metric:
            query += " AND metric = ?"
            params.append(metric)

        if year is not None:
            query += " AND year = ?"
            params.append(year)

        query += " ORDER BY year DESC, metric"

        rows = connection.execute(query, params).fetchall()

        results = [dict(row) for row in rows]

        return {
            "company_id": company_id.upper(),
            "count": len(results),
            "results": results,
        }

    finally:
        connection.close()
