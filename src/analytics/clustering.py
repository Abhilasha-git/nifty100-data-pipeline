from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"

OUTPUT_DIR = BASE_DIR / "output"
REPORTS_DIR = BASE_DIR / "reports"

CLUSTER_OUTPUT = OUTPUT_DIR / "cluster_labels.csv"
ELBOW_OUTPUT = REPORTS_DIR / "elbow_plot.png"

N_CLUSTERS = 5
RANDOM_STATE = 42

FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


# ---------------------------------------------------------------------------
# Database loading
# ---------------------------------------------------------------------------


def load_company_data() -> pd.DataFrame:
    """Load latest company clustering features from SQLite."""

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"SQLite database not found: {DB_PATH}"
        )

    query = """
        WITH latest_ratios AS (
            SELECT
                fr.company_id,
                fr.year,
                fr.return_on_equity_pct,
                fr.debt_to_equity,
                fr.revenue_cagr_5yr,
                fr.operating_profit_margin_pct
            FROM financial_ratios AS fr
            INNER JOIN (
                SELECT
                    company_id,
                    MAX(year) AS latest_year
                FROM financial_ratios
                GROUP BY company_id
            ) AS latest
                ON fr.company_id = latest.company_id
                AND fr.year = latest.latest_year
        ),

        latest_cashflow AS (
            SELECT
                cf.company_id,
                cf.year,
                cf.net_cash_flow
            FROM cashflow AS cf
            INNER JOIN (
                SELECT
                    company_id,
                    MAX(year) AS latest_year
                FROM cashflow
                GROUP BY company_id
            ) AS latest_cf
                ON cf.company_id = latest_cf.company_id
                AND cf.year = latest_cf.latest_year
        ),

        five_year_cashflow AS (
            SELECT
                latest.company_id,
                latest.year AS latest_year,
                latest.net_cash_flow AS latest_fcf,
                old.net_cash_flow AS old_fcf,
                old.year AS old_year
            FROM latest_cashflow AS latest
            LEFT JOIN cashflow AS old
                ON old.company_id = latest.company_id
                AND old.year = latest.year - 5
        ),

        peer_groups AS (
            SELECT
                company_id,
                peer_group_name
            FROM peer_percentiles
            WHERE metric = 'ROE'
            GROUP BY company_id
        )

        SELECT
            lr.company_id,
            COALESCE(
                pg.peer_group_name,
                'Unknown'
            ) AS broad_sector,
            lr.year,
            lr.return_on_equity_pct,
            lr.debt_to_equity,
            lr.revenue_cagr_5yr,
            CASE
                WHEN fc.old_fcf IS NOT NULL
                    AND fc.latest_fcf IS NOT NULL
                    AND fc.old_fcf > 0
                    AND fc.latest_fcf > 0
                THEN (
                    POWER(
                        CAST(fc.latest_fcf AS REAL)
                        / CAST(fc.old_fcf AS REAL),
                        1.0 / 5.0
                    ) - 1.0
                ) * 100.0
                ELSE NULL
            END AS fcf_cagr_5yr,
            lr.operating_profit_margin_pct
        FROM latest_ratios AS lr
        LEFT JOIN five_year_cashflow AS fc
            ON lr.company_id = fc.company_id
            AND lr.year = fc.latest_year
        LEFT JOIN peer_groups AS pg
            ON lr.company_id = pg.company_id
    """

    with sqlite3.connect(DB_PATH) as connection:
        df = pd.read_sql_query(
            query,
            connection,
        )

    if df.empty:
        raise ValueError(
            "No clustering data returned from the database."
        )

    return df


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Impute missing clustering features using sector medians."""

    required_columns = [
        "company_id",
        "broad_sector",
        *FEATURES,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    working = df[required_columns].copy()

    for feature in FEATURES:
        working[feature] = pd.to_numeric(
            working[feature],
            errors="coerce",
        )

        # Impute missing values using the peer-group/sector median.
        working[feature] = (
            working
            .groupby("broad_sector")[feature]
            .transform(
                lambda series: series.fillna(series.median())
            )
        )

        # If an entire group is missing the feature,
        # fall back to the overall median.
        overall_median = working[feature].median()

        working[feature] = working[feature].fillna(
            overall_median
        )

        BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"

OUTPUT_DIR = BASE_DIR / "output"
REPORTS_DIR = BASE_DIR / "reports"

CLUSTER_OUTPUT = OUTPUT_DIR / "cluster_labels.csv"
ELBOW_OUTPUT = REPORTS_DIR / "elbow_plot.png"

N_CLUSTERS = 5
RANDOM_STATE = 42

FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


# ---------------------------------------------------------------------------
# Database loading
# ---------------------------------------------------------------------------


def load_company_data() -> pd.DataFrame:
    """Load latest company clustering features from SQLite."""

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"SQLite database not found: {DB_PATH}"
        )

    query = """
        WITH latest_ratios AS (
            SELECT
                fr.company_id,
                fr.year,
                fr.return_on_equity_pct,
                fr.debt_to_equity,
                fr.revenue_cagr_5yr,
                fr.operating_profit_margin_pct
            FROM financial_ratios AS fr
            INNER JOIN (
                SELECT
                    company_id,
                    MAX(year) AS latest_year
                FROM financial_ratios
                GROUP BY company_id
            ) AS latest
                ON fr.company_id = latest.company_id
                AND fr.year = latest.latest_year
        ),

        latest_cashflow AS (
            SELECT
                cf.company_id,
                cf.year,
                cf.net_cash_flow
            FROM cashflow AS cf
            INNER JOIN (
                SELECT
                    company_id,
                    MAX(year) AS latest_year
                FROM cashflow
                GROUP BY company_id
            ) AS latest_cf
                ON cf.company_id = latest_cf.company_id
                AND cf.year = latest_cf.latest_year
        ),

        five_year_cashflow AS (
            SELECT
                latest.company_id,
                latest.year AS latest_year,
                latest.net_cash_flow AS latest_fcf,
                old.net_cash_flow AS old_fcf,
                old.year AS old_year
            FROM latest_cashflow AS latest
            LEFT JOIN cashflow AS old
                ON old.company_id = latest.company_id
                AND old.year = latest.year - 5
        ),

        peer_groups AS (
            SELECT
                company_id,
                peer_group_name
            FROM peer_percentiles
            WHERE metric = 'ROE'
            GROUP BY company_id
        )

        SELECT
            lr.company_id,
            COALESCE(
                pg.peer_group_name,
                'Unknown'
            ) AS broad_sector,
            lr.year,
            lr.return_on_equity_pct,
            lr.debt_to_equity,
            lr.revenue_cagr_5yr,
            CASE
                WHEN fc.old_fcf IS NOT NULL
                    AND fc.latest_fcf IS NOT NULL
                    AND fc.old_fcf > 0
                    AND fc.latest_fcf > 0
                THEN (
                    POWER(
                        CAST(fc.latest_fcf AS REAL)
                        / CAST(fc.old_fcf AS REAL),
                        1.0 / 5.0
                    ) - 1.0
                ) * 100.0
                ELSE NULL
            END AS fcf_cagr_5yr,
            lr.operating_profit_margin_pct
        FROM latest_ratios AS lr
        LEFT JOIN five_year_cashflow AS fc
            ON lr.company_id = fc.company_id
            AND lr.year = fc.latest_year
        LEFT JOIN peer_groups AS pg
            ON lr.company_id = pg.company_id
    """

    with sqlite3.connect(DB_PATH) as connection:
        df = pd.read_sql_query(
            query,
            connection,
        )

    if df.empty:
        raise ValueError(
            "No clustering data returned from the database."
        )

    return df


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Impute missing clustering features using sector medians."""

    required_columns = [
        "company_id",
        "broad_sector",
        *FEATURES,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    working = df[required_columns].copy()

    for feature in FEATURES:
        working[feature] = pd.to_numeric(
            working[feature],
            errors="coerce",
        )

        # Impute missing values using the peer-group/sector median.
        working[feature] = (
            working
            .groupby("broad_sector")[feature]
            .transform(
                lambda series: series.fillna(series.median())
            )
        )

        # If an entire group is missing the feature,
        # fall back to the overall median.
        overall_median = working[feature].median()

        working[feature] = working[feature].fillna(
            overall_median
        )

    if "return_on_equity_pct" in working.columns:

        roe_cap = working["return_on_equity_pct"].quantile(0.90)

        extreme_roe = (
            working["return_on_equity_pct"] > roe_cap
        )

        if extreme_roe.any():
            print(
                f"ROE cap applied at {roe_cap:.2f}% "
                f"to {extreme_roe.sum()} companies:"
            )

            for _, row in working.loc[
                extreme_roe,
                ["company_id", "return_on_equity_pct"],
            ].iterrows():

                print(
                    f"{row['company_id']}: "
                    f"{row['return_on_equity_pct']:.2f}% "
                    f"-> {roe_cap:.2f}%"
                )

            working["return_on_equity_pct"] = (
                working["return_on_equity_pct"]
                .clip(upper=roe_cap)
            )

    # Make sure no feature is still missing.
    if working[FEATURES].isna().any().any():
        missing = working[FEATURES].isna().sum()

        raise ValueError(
            "Unable to impute all missing values:\n"
            f"{missing}"
        )
        """
    roe_upper = working["return_on_equity_pct"].quantile(0.95)

    roe_before = working["return_on_equity_pct"].copy()

    working["return_on_equity_pct"] = (
        working["return_on_equity_pct"]
        .clip(upper=roe_upper)
    )

    capped = working.loc[
        roe_before > roe_upper,
        ["company_id"]
    ].copy()

    if not capped.empty:
        print(
            f"ROE cap applied at {roe_upper:.2f}% "
            f"to {len(capped)} companies:"
        )

        for company_id in capped["company_id"]:
            before = roe_before.loc[
                working["company_id"] == company_id
        ].iloc[0]

        print(
            f"  {company_id}: "
            f"{before:.2f}% -> {roe_upper:.2f}%"
        )
    """
    return working


# ---------------------------------------------------------------------------
# KMeans
# ---------------------------------------------------------------------------


def run_kmeans(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, KMeans, StandardScaler]:
    """Run reproducible five-cluster KMeans."""

    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        df[FEATURES]
    )

    model = KMeans(
        n_clusters=N_CLUSTERS,
        random_state=RANDOM_STATE,
        n_init=10,
    )

    cluster_ids = model.fit_predict(
        scaled_features
    )

    result = df.copy()

    result["cluster_id"] = cluster_ids

    # Calculate distance from assigned centroid.
    centroids = model.cluster_centers_

    distances = []

    for row, cluster_id in zip(
        scaled_features,
        cluster_ids,
    ):
        centroid = centroids[cluster_id]

        distance = (
            ((row - centroid) ** 2).sum() ** 0.5
        )

        distances.append(distance)

    result["distance_from_centroid"] = distances

    return result, model, scaler


# ---------------------------------------------------------------------------
# Cluster naming
# ---------------------------------------------------------------------------


def assign_cluster_names(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[int, str]]:
    """Assign descriptive names to the five clusters."""

    profile = df.groupby("cluster_id")[FEATURES].mean()

    names: dict[int, str] = {}

    # High-quality companies.
    quality_score = (
        profile["return_on_equity_pct"].rank(pct=True)
        + profile["revenue_cagr_5yr"].rank(pct=True)
        + profile["fcf_cagr_5yr"].rank(pct=True)
        + profile["operating_profit_margin_pct"].rank(pct=True)
        - profile["debt_to_equity"].rank(pct=True)
    )

    highest_quality = quality_score.idxmax()

    names[highest_quality] = "High-Quality Compounders"

    remaining = [
        cluster
        for cluster in profile.index
        if cluster not in names
    ]

    # Strong growth companies.
    growth_score = (
        profile["revenue_cagr_5yr"]
        + profile["fcf_cagr_5yr"]
    )

    growth_cluster = growth_score.loc[remaining].idxmax()

    names[growth_cluster] = "Emerging Growth"

    remaining = [
        cluster
        for cluster in profile.index
        if cluster not in names
    ]

    # High debt and weak profitability.
    distress_score = (
        profile["debt_to_equity"].rank(pct=True)
        - profile["operating_profit_margin_pct"].rank(pct=True)
        - profile["return_on_equity_pct"].rank(pct=True)
    )

    distress_cluster = distress_score.loc[remaining].idxmax()

    names[distress_cluster] = "Distressed or Turnaround"

    remaining = [
        cluster
        for cluster in profile.index
        if cluster not in names
    ]

    # Lowest growth.
    if remaining:
        low_growth_cluster = (
            profile["revenue_cagr_5yr"]
            + profile["fcf_cagr_5yr"]
        ).loc[remaining].idxmin()

        names[low_growth_cluster] = (
            "Defensive Dividend Payers"
        )

    remaining = [
        cluster
        for cluster in profile.index
        if cluster not in names
    ]

    if remaining:
        names[remaining[0]] = "Value Cyclicals"

    result = df.copy()

    result["cluster_name"] = result[
        "cluster_id"
    ].map(names)

    return result, names


# ---------------------------------------------------------------------------
# Elbow plot
# ---------------------------------------------------------------------------


def generate_elbow_plot(
    scaled_features,
) -> list[tuple[int, float]]:
    """Generate KMeans elbow plot for k=2 through k=10."""

    ks = range(2, 11)

    inertias = []

    for k in ks:
        model = KMeans(
            n_clusters=k,
            random_state=RANDOM_STATE,
            n_init=10,
        )

        model.fit(scaled_features)

        inertias.append(model.inertia_)

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(figsize=(10, 6))

    plt.plot(
        list(ks),
        inertias,
        marker="o",
    )

    plt.axvline(
        N_CLUSTERS,
        linestyle="--",
        label="Selected k=5",
    )

    plt.title("KMeans Elbow Plot")
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Inertia")
    plt.xticks(list(ks))
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        ELBOW_OUTPUT,
        dpi=150,
    )

    plt.close()

    return list(zip(ks, inertias))


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def save_cluster_labels(
    df: pd.DataFrame,
) -> None:
    """Save company cluster assignments to CSV."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = df[
        [
            "company_id",
            "cluster_id",
            "cluster_name",
            "distance_from_centroid",
        ]
    ].copy()

    output.to_csv(
        CLUSTER_OUTPUT,
        index=False,
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_output(
    df: pd.DataFrame,
) -> None:
    """Validate that all 92 companies have cluster assignments."""

    if len(df) != 92:
        raise ValueError(
            f"Expected 92 company records, found {len(df)}."
        )

    if df["company_id"].nunique() != 92:
        raise ValueError(
            "Expected 92 unique company IDs."
        )

    if df["cluster_id"].isna().any():
        raise ValueError(
            "Some companies have no cluster assignment."
        )

    valid_clusters = set(range(N_CLUSTERS))

    actual_clusters = set(
        df["cluster_id"].unique()
    )

    if actual_clusters != valid_clusters:
        raise ValueError(
            f"Expected clusters {valid_clusters}, "
            f"found {actual_clusters}."
        )

    if df["cluster_name"].isna().any():
        raise ValueError(
            "Some companies have no cluster name."
        )

    print("Validation passed.")
    print(f"Companies: {len(df)}")
    print(
        f"Unique companies: "
        f"{df['company_id'].nunique()}"
    )
    print(
        f"Clusters: "
        f"{sorted(actual_clusters)}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the complete KMeans clustering pipeline."""

    print("Loading company data...")

    raw_data = load_company_data()

    print(
        f"Loaded {len(raw_data)} rows."
    )

    # Keep latest record for each company.
    if "year" in raw_data.columns:
        raw_data = (
            raw_data
            .sort_values("year")
            .drop_duplicates(
                subset=["company_id"],
                keep="last",
            )
        )

    print("Preparing features...")

    prepared = prepare_features(
        raw_data
    )

    print("Scaling features...")

    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        prepared[FEATURES]
    )

    print("Generating elbow plot...")

    elbow_results = generate_elbow_plot(
        scaled_features
    )

    print("\nElbow results:")

    for k, inertia in elbow_results:
        print(
            f"  k={k}: inertia={inertia:.2f}"
        )

    print("\nRunning KMeans with k=5...")

    clustered, _, _ = run_kmeans(
        prepared
    )

    print("Assigning cluster names...")

    clustered, cluster_names = (
        assign_cluster_names(
            clustered
        )
    )

    print("\nCluster names:")

    for cluster_id, name in sorted(
        cluster_names.items()
    ):
        count = (
            clustered["cluster_id"]
            == cluster_id
        ).sum()

        print(
            f"  Cluster {cluster_id}: "
            f"{name} ({count} companies)"
        )

    print("\nSaving cluster labels...")

    save_cluster_labels(
        clustered
    )

    print("\nValidating output...")

    validate_output(
        clustered
    )

    print("\nDone.")

    print(
        f"Cluster labels: {CLUSTER_OUTPUT}"
    )

    print(
        f"Elbow plot: {ELBOW_OUTPUT}"
    )


if __name__ == "__main__":
    main()

    # Make sure no feature is still missing.
    if working[FEATURES].isna().any().any():
        missing = working[FEATURES].isna().sum()

        raise ValueError(
            "Unable to impute all missing values:\n"
            f"{missing}"
        )

    roe_upper = working["return_on_equity_pct"].quantile(0.95)

    roe_before = working["return_on_equity_pct"].copy()

    working["return_on_equity_pct"] = (
        working["return_on_equity_pct"]
        .clip(upper=roe_upper)
    )

    capped = working.loc[
        roe_before > roe_upper,
        ["company_id"]
    ].copy()

    if not capped.empty:
        print(
            f"ROE cap applied at {roe_upper:.2f}% "
            f"to {len(capped)} companies:"
        )

        for company_id in capped["company_id"]:
            before = roe_before.loc[
                working["company_id"] == company_id
        ].iloc[0]

        print(
            f"  {company_id}: "
            f"{before:.2f}% -> {roe_upper:.2f}%"
        )

    return working


# ---------------------------------------------------------------------------
# KMeans
# ---------------------------------------------------------------------------


def run_kmeans(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, KMeans, StandardScaler]:
    """Run reproducible five-cluster KMeans."""

    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        df[FEATURES]
    )

    model = KMeans(
        n_clusters=N_CLUSTERS,
        random_state=RANDOM_STATE,
        n_init=10,
    )

    cluster_ids = model.fit_predict(
        scaled_features
    )

    result = df.copy()

    result["cluster_id"] = cluster_ids

    # Calculate distance from assigned centroid.
    centroids = model.cluster_centers_

    distances = []

    for row, cluster_id in zip(
        scaled_features,
        cluster_ids,
    ):
        centroid = centroids[cluster_id]

        distance = (
            ((row - centroid) ** 2).sum() ** 0.5
        )

        distances.append(distance)

    result["distance_from_centroid"] = distances

    return result, model, scaler


# ---------------------------------------------------------------------------
# Cluster naming
# ---------------------------------------------------------------------------


def assign_cluster_names(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[int, str]]:
    """Assign descriptive names to the five clusters."""

    profile = df.groupby("cluster_id")[FEATURES].mean()

    names: dict[int, str] = {}

    # High-quality companies.
    quality_score = (
        profile["return_on_equity_pct"].rank(pct=True)
        + profile["revenue_cagr_5yr"].rank(pct=True)
        + profile["fcf_cagr_5yr"].rank(pct=True)
        + profile["operating_profit_margin_pct"].rank(pct=True)
        - profile["debt_to_equity"].rank(pct=True)
    )

    highest_quality = quality_score.idxmax()

    names[highest_quality] = "High-Quality Compounders"

    remaining = [
        cluster
        for cluster in profile.index
        if cluster not in names
    ]

    # Strong growth companies.
    growth_score = (
        profile["revenue_cagr_5yr"]
        + profile["fcf_cagr_5yr"]
    )

    growth_cluster = growth_score.loc[remaining].idxmax()

    names[growth_cluster] = "Emerging Growth"

    remaining = [
        cluster
        for cluster in profile.index
        if cluster not in names
    ]

    # High debt and weak profitability.
    distress_score = (
        profile["debt_to_equity"].rank(pct=True)
        - profile["operating_profit_margin_pct"].rank(pct=True)
        - profile["return_on_equity_pct"].rank(pct=True)
    )

    distress_cluster = distress_score.loc[remaining].idxmax()

    names[distress_cluster] = "Distressed or Turnaround"

    remaining = [
        cluster
        for cluster in profile.index
        if cluster not in names
    ]

    # Lowest growth.
    if remaining:
        low_growth_cluster = (
            profile["revenue_cagr_5yr"]
            + profile["fcf_cagr_5yr"]
        ).loc[remaining].idxmin()

        names[low_growth_cluster] = (
            "Defensive Dividend Payers"
        )

    remaining = [
        cluster
        for cluster in profile.index
        if cluster not in names
    ]

    if remaining:
        names[remaining[0]] = "Value Cyclicals"

    result = df.copy()

    result["cluster_name"] = result[
        "cluster_id"
    ].map(names)

    return result, names


# ---------------------------------------------------------------------------
# Elbow plot
# ---------------------------------------------------------------------------


def generate_elbow_plot(
    scaled_features,
) -> list[tuple[int, float]]:
    """Generate KMeans elbow plot for k=2 through k=10."""

    ks = range(2, 11)

    inertias = []

    for k in ks:
        model = KMeans(
            n_clusters=k,
            random_state=RANDOM_STATE,
            n_init=10,
        )

        model.fit(scaled_features)

        inertias.append(model.inertia_)

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(figsize=(10, 6))

    plt.plot(
        list(ks),
        inertias,
        marker="o",
    )

    plt.axvline(
        N_CLUSTERS,
        linestyle="--",
        label="Selected k=5",
    )

    plt.title("KMeans Elbow Plot")
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Inertia")
    plt.xticks(list(ks))
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        ELBOW_OUTPUT,
        dpi=150,
    )

    plt.close()

    return list(zip(ks, inertias))


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def save_cluster_labels(
    df: pd.DataFrame,
) -> None:
    """Save company cluster assignments to CSV."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = df[
        [
            "company_id",
            "cluster_id",
            "cluster_name",
            "distance_from_centroid",
        ]
    ].copy()

    output.to_csv(
        CLUSTER_OUTPUT,
        index=False,
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_output(
    df: pd.DataFrame,
) -> None:
    """Validate that all 92 companies have cluster assignments."""

    if len(df) != 92:
        raise ValueError(
            f"Expected 92 company records, found {len(df)}."
        )

    if df["company_id"].nunique() != 92:
        raise ValueError(
            "Expected 92 unique company IDs."
        )

    if df["cluster_id"].isna().any():
        raise ValueError(
            "Some companies have no cluster assignment."
        )

    valid_clusters = set(range(N_CLUSTERS))

    actual_clusters = set(
        df["cluster_id"].unique()
    )

    if actual_clusters != valid_clusters:
        raise ValueError(
            f"Expected clusters {valid_clusters}, "
            f"found {actual_clusters}."
        )

    if df["cluster_name"].isna().any():
        raise ValueError(
            "Some companies have no cluster name."
        )

    print("Validation passed.")
    print(f"Companies: {len(df)}")
    print(
        f"Unique companies: "
        f"{df['company_id'].nunique()}"
    )
    print(
        f"Clusters: "
        f"{sorted(actual_clusters)}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the complete KMeans clustering pipeline."""

    print("Loading company data...")

    raw_data = load_company_data()

    print(
        f"Loaded {len(raw_data)} rows."
    )

    # Keep latest record for each company.
    if "year" in raw_data.columns:
        raw_data = (
            raw_data
            .sort_values("year")
            .drop_duplicates(
                subset=["company_id"],
                keep="last",
            )
        )

    print("Preparing features...")

    prepared = prepare_features(
        raw_data
    )

    print("Scaling features...")

    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        prepared[FEATURES]
    )

    print("Generating elbow plot...")

    elbow_results = generate_elbow_plot(
        scaled_features
    )

    print("\nElbow results:")

    for k, inertia in elbow_results:
        print(
            f"  k={k}: inertia={inertia:.2f}"
        )

    print("\nRunning KMeans with k=5...")

    clustered, _, _ = run_kmeans(
        prepared
    )

    print("Assigning cluster names...")

    clustered, cluster_names = (
        assign_cluster_names(
            clustered
        )
    )

    print("\nCluster names:")

    for cluster_id, name in sorted(
        cluster_names.items()
    ):
        count = (
            clustered["cluster_id"]
            == cluster_id
        ).sum()

        print(
            f"  Cluster {cluster_id}: "
            f"{name} ({count} companies)"
        )

    print("\nSaving cluster labels...")

    save_cluster_labels(
        clustered
    )

    print("\nValidating output...")

    validate_output(
        clustered
    )

    print("\nDone.")

    print(
        f"Cluster labels: {CLUSTER_OUTPUT}"
    )

    print(
        f"Elbow plot: {ELBOW_OUTPUT}"
    )


if __name__ == "__main__":
    main()
