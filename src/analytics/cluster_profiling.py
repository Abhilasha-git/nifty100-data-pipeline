from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import zscore


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"

CLUSTER_FILE = BASE_DIR / "output" / "cluster_labels.csv"

OUTLIER_OUTPUT = BASE_DIR / "output" / "outlier_report.csv"
PORTFOLIO_OUTPUT = BASE_DIR / "output" / "portfolio_stats.csv"
HEATMAP_OUTPUT = BASE_DIR / "reports" / "correlation_heatmap.png"


# Ten KPIs required for the correlation matrix and portfolio statistics.
KPI_COLUMNS = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "return_on_assets_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
]


# Five clustering features.
CLUSTER_FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "operating_profit_margin_pct",
]


# ---------------------------------------------------------------------------
# Database loading
# ---------------------------------------------------------------------------

def load_latest_kpis() -> pd.DataFrame:
    """Load the latest financial KPIs for all companies."""

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    query = """
        SELECT
            fr.company_id,
            fr.year,
            fr.return_on_equity_pct,
            fr.return_on_capital_employed_pct,
            fr.return_on_assets_pct,
            fr.net_profit_margin_pct,
            fr.operating_profit_margin_pct,
            fr.debt_to_equity,
            fr.interest_coverage,
            fr.asset_turnover,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr
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
    """

    with sqlite3.connect(DB_PATH) as connection:
        df = pd.read_sql_query(
            query,
            connection,
        )

    if df.empty:
        raise ValueError(
            "No financial KPI data was returned."
        )

    return df


# ---------------------------------------------------------------------------
# Cluster profiling
# ---------------------------------------------------------------------------

def generate_cluster_profile(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Generate mean and median KPI profiles for each cluster."""

    print("Generating cluster profiles...")

    profile_features = [
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "operating_profit_margin_pct",
    ]

    required_columns = [
        "cluster_id",
        "cluster_name",
        *profile_features,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    working = df[
        required_columns
    ].copy()

    # Convert clustering/profile features to numeric.
    for feature in profile_features:
        working[feature] = pd.to_numeric(
            working[feature],
            errors="coerce",
        )


def generate_cluster_profile(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Generate mean and median KPI profiles for each cluster."""

    print("Generating cluster profiles...")

    profile_features = [
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "operating_profit_margin_pct",
    ]

    required_columns = [
        "cluster_id",
        "cluster_name",
        *profile_features,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    working = df[required_columns].copy()

    # Convert profile features to numeric.
    for feature in profile_features:
        working[feature] = pd.to_numeric(
            working[feature],
            errors="coerce",
        )

    # ---------------------------------------------------------
    # CAP EXTREME ROE VALUES FOR CLUSTER PROFILE
    # ---------------------------------------------------------
    if "return_on_equity_pct" in working.columns:

        roe_cap = working["return_on_equity_pct"].quantile(0.90)

        working["return_on_equity_pct"] = (
            working["return_on_equity_pct"]
            .clip(upper=roe_cap)
        )

        print(
            f"ROE cap applied to cluster profile at "
            f"{roe_cap:.2f}%"
        )

    print("Cluster feature dtypes:")
    print(working[profile_features].dtypes)

    # Generate mean and median for each cluster.
    profile = (
        working
        .groupby(
            ["cluster_id", "cluster_name"],
            sort=True,
        )[profile_features]
        .agg(["mean", "median"])
        .round(2)
    )

    print()
    print(profile.to_string())


    """
    print("Cluster feature dtypes:")
    print(working[profile_features].dtypes)

    # Generate mean and median for each cluster.
    profile = (
        working
        .groupby(
            ["cluster_id", "cluster_name"],
            sort=True,
        )[profile_features]
        .agg(["mean", "median"])
        .round(2)
    )

    print()
    print(profile.to_string())


    if "return_on_equity_pct" in working.columns:
        roe_cap = working["return_on_equity_pct"].quantile(0.90)

        working["return_on_equity_pct"] = (
            working["return_on_equity_pct"]
            .clip(upper=roe_cap)
        )

        print(
            f"ROE cap applied at {roe_cap:.2f}%"
        )

    print("Cluster feature dtypes:")
    print(working[profile_features].dtypes)
    # Generate mean and median for each cluster.
    profile = (
        working
        .groupby(
            ["cluster_id", "cluster_name"],
            sort=True,
        )[profile_features]
        .agg(["mean", "median"])
        .round(2)
    )

    print()
    print(profile.to_string())
    """
    return profile

def print_cluster_profile(profile: pd.DataFrame) -> None:
    """Print cluster financial profiles to the console."""

    print("\n" + "=" * 80)
    print("CLUSTER PROFILE")
    print("=" * 80)

    print(profile.round(2).to_string())

    print("\n")


# ---------------------------------------------------------------------------
# Correlation matrix
# ---------------------------------------------------------------------------

def generate_correlation_heatmap(
    df: pd.DataFrame,
) -> None:
    """Generate Pearson correlation heatmap for ten KPIs."""

    numeric = df[KPI_COLUMNS].apply(
        pd.to_numeric,
        errors="coerce",
    )

    correlation = numeric.corr(
        method="pearson"
    )

    HEATMAP_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(
        figsize=(14, 11)
    )

    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=0.5,
    )

    plt.title(
        "Pearson Correlation Matrix — Latest Year KPIs"
    )

    plt.tight_layout()

    plt.savefig(
        HEATMAP_OUTPUT,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"Correlation heatmap saved to: "
        f"{HEATMAP_OUTPUT}"
    )


# ---------------------------------------------------------------------------
# Outlier detection
# ---------------------------------------------------------------------------

def generate_outlier_report(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Detect KPI outliers using sector-level absolute Z-score above 3."""

    working = df.copy()

    records = []

    # Use cluster_name as the available sector/group classification.
    group_column = "cluster_name"

    for group_name, group in working.groupby(
        group_column
    ):

        for metric in KPI_COLUMNS:

            values = pd.to_numeric(
                group[metric],
                errors="coerce",
            )

            valid = values.notna()

            if valid.sum() < 3:
                continue

            mean = values[valid].mean()
            std = values[valid].std(ddof=0)

            if std == 0:
                continue

            z_scores = (
                values - mean
            ) / std

            for index in z_scores.index:

                z = z_scores.loc[index]

                if pd.isna(z):
                    continue

                if abs(z) > 3:

                    records.append(
                        {
                            "company_id": working.loc[
                                index,
                                "company_id",
                            ],
                            "broad_sector": group_name,
                            "metric": metric,
                            "value": working.loc[
                                index,
                                metric,
                            ],
                            "z_score": z,
                        }
                    )

    result = pd.DataFrame(
        records,
        columns=[
            "company_id",
            "broad_sector",
            "metric",
            "value",
            "z_score",
        ],
    )

    OUTLIER_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTLIER_OUTPUT,
        index=False,
    )

    print(
        f"Outlier report saved to: "
        f"{OUTLIER_OUTPUT}"
    )

    print(
        f"Outlier records: {len(result)}"
    )

    return result


# ---------------------------------------------------------------------------
# Portfolio statistics
# ---------------------------------------------------------------------------

def generate_portfolio_stats(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Generate P10 through P90 and descriptive statistics for ten KPIs."""

    records = []

    for metric in KPI_COLUMNS:

        values = pd.to_numeric(
            df[metric],
            errors="coerce",
        ).dropna()

        if values.empty:
            continue

        records.append(
            {
                "kpi": metric,
                "P10": values.quantile(0.10),
                "P25": values.quantile(0.25),
                "P50": values.quantile(0.50),
                "P75": values.quantile(0.75),
                "P90": values.quantile(0.90),
                "Mean": values.mean(),
                "Std": values.std(),
            }
        )

    result = pd.DataFrame(
        records
    )

    PORTFOLIO_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        PORTFOLIO_OUTPUT,
        index=False,
    )

    print(
        f"Portfolio statistics saved to: "
        f"{PORTFOLIO_OUTPUT}"
    )

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the complete Day 37 profiling pipeline."""

    print("Loading latest KPI data...")

    kpis = load_latest_kpis()

    print(
        f"Loaded {len(kpis)} company KPI records."
    )

    print(
        "Loading cluster assignments..."
    )

    clusters = pd.read_csv(
        CLUSTER_FILE
    )

    df = clusters.merge(
        kpis,
        on="company_id",
        how="left",
    )

    print(
        f"Merged dataset contains {len(df)} rows."
    )

    if df["company_id"].nunique() != 92:
        raise ValueError(
            "Expected 92 unique companies, "
            f"found {df['company_id'].nunique()}."
        )

    # ---------------------------------------------------------------
    # Cluster profiling
    # ---------------------------------------------------------------

    print(
        "\nGenerating cluster profiles..."
    )

    profile = generate_cluster_profile(df)

    print_cluster_profile(
        profile
    )

    # ---------------------------------------------------------------
    # Correlation heatmap
    # ---------------------------------------------------------------

    print(
        "Generating correlation heatmap..."
    )

    generate_correlation_heatmap(
        df
    )

    # ---------------------------------------------------------------
    # Outlier detection
    # ---------------------------------------------------------------

    print(
        "Generating outlier report..."
    )

    generate_outlier_report(
        df
    )

    # ---------------------------------------------------------------
    # Portfolio statistics
    # ---------------------------------------------------------------

    print(
        "Generating portfolio statistics..."
    )

    stats = generate_portfolio_stats(
        df
    )

    print("\nPortfolio statistics:")
    print(
        stats.round(2).to_string(
            index=False
        )
    )

    print(
        "\n" + "=" * 80
    )

    print(
        "DAY 37 PROFILING COMPLETE"
    )

    print(
        "=" * 80
    )

    print(
        f"Cluster profile: generated"
    )

    print(
        f"Correlation heatmap: {HEATMAP_OUTPUT}"
    )

    print(
        f"Outlier report: {OUTLIER_OUTPUT}"
    )

    print(
        f"Portfolio statistics: {PORTFOLIO_OUTPUT}"
    )


if __name__ == "__main__":
    main()
