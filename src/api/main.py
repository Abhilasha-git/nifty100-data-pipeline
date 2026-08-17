import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import (
    companies,
    screener,
    sectors,
    peers,
    valuation,
    portfolio,
    documents,
)

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

from src.api.database import get_db_connection

VERSION = "1.0.0"

START_TIME = time.time()


# -------------------------------------------------------------------
# FastAPI application
# -------------------------------------------------------------------

app = FastAPI(
    title="Nifty 100 Data Pipeline API",
    description="REST API for Nifty 100 financial analytics",
    version=VERSION,
)


# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(companies.router, prefix="/api/v1")
app.include_router(screener.router, prefix="/api/v1")
app.include_router(sectors.router, prefix="/api/v1")
app.include_router(peers.router, prefix="/api/v1")
app.include_router(valuation.router, prefix="/api/v1")
app.include_router(portfolio.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")



# -------------------------------------------------------------------
# Request logging middleware
# -------------------------------------------------------------------

@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next,
):
    """Log HTTP method, path, and response time."""

    start = time.perf_counter()

    response = await call_next(request)

    elapsed = time.perf_counter() - start

    print(
        f"{request.method} "
        f"{request.url.path} "
        f"{response.status_code} "
        f"{elapsed:.4f}s"
    )

    return response


# -------------------------------------------------------------------
# Health endpoint
# -------------------------------------------------------------------

@app.get("/api/v1/health")
def health_check():
    """Return API and database health information."""

    connection = get_db_connection()

    try:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        ).fetchall()

        db_row_counts = {}

        for table in tables:
            table_name = table["name"]

            count = connection.execute(
                f'SELECT COUNT(*) AS count FROM "{table_name}"'
            ).fetchone()["count"]

            db_row_counts[table_name] = count

    finally:
        connection.close()

    return {
        "status": "ok",
        "db_row_counts": db_row_counts,
        "uptime_seconds": round(
            time.time() - START_TIME,
            2,
        ),
        "version": VERSION,
    }