import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"


def add_peer_summary(df):

    conn = sqlite3.connect(DB_PATH)

    peer_df = pd.read_sql(
        """
        SELECT *
        FROM peer_percentiles
        """,
        conn,
    )

    conn.close()

    summary = (
        peer_df
        .groupby(["company_id", "year"])
        .agg(
            peer_percentile_score=("percentile_rank", "mean"),
            best_metric=("percentile_rank", "max"),
            weakest_metric=("percentile_rank", "min"),
        )
        .reset_index()
    )
    
    # ---------- ADD THESE ----------
    print("\nMain dataframe dtypes:")
    print(df.dtypes)

    print("\nSummary dataframe dtypes:")
    print(summary.dtypes)

    print("\nMain company_id:")
    print(df["company_id"].head())

    print("\nSummary company_id:")
    print(summary["company_id"].head())

    print("\nMain year:")
    print(df["year"].head())

    print("\nSummary year:")
    print(summary["year"].head())
    # -------------------------------
    
    df = df.merge(
        summary,
        on=["company_id", "year"],
        how="left",
    )
    
   
    return df