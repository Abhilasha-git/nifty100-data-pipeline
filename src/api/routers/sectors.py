import sqlite3

from fastapi import APIRouter

from src.api.database import get_db_connection

router = APIRouter(
    prefix="/sectors",
    tags=["Sectors"],
)


@router.get("")
def list_sectors():
    """
    Return available sectors.

    Note:
    The current database schema does not show a sector column
    in the companies table, so this endpoint currently returns
    a clear scaffold response.
    """

    return {
        "count": 0,
        "results": [],
        "message": "Sector data is not available in the current database schema.",
    }