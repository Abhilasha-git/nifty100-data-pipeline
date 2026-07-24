import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"


def load_peer_percentiles():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        "SELECT * FROM peer_percentiles",
        conn,
    )

    conn.close()

    return df

def average_peer_score(peer_df):

    return (
        peer_df
        .groupby(["company_id", "year"])
        ["percentile_rank"]
        .mean()
        .reset_index(name="peer_percentile_score")
    )