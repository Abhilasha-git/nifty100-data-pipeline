cursor.execute("""
CREATE TABLE IF NOT EXISTS peer_percentiles (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    company_id TEXT,

    peer_group_name TEXT,

    metric TEXT,

    value REAL,

    percentile_rank REAL,

    year INTEGER

)
""")