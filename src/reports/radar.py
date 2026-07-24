from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

print("Loaded radar.py")
print(__file__)
OUTPUT_DIR = Path("reports/radar_charts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


METRICS = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "composite_quality_score",
]

LABELS = [
    "ROE",
    "ROCE",
    "NPM",
    "D/E",
    "FCF",
    "PAT CAGR",
    "Revenue CAGR",
    "Composite",
]


def generate_radar_charts(df):
    """
    Generate one radar chart per company.
    """
    print("Inside generate_radar_charts")
    grouped = df.groupby("peer_group_name", dropna=False)
    print(df["peer_group_name"].value_counts(dropna=False))

    df = df.copy()

    # convert metrics to numeric
    for col in METRICS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    nifty_avg = df[METRICS].mean()

    # -----------------------------
    # Companies WITH peer groups
    # -----------------------------
    grouped = df.groupby("peer_group_name", dropna=False)

    for peer_name, peer_df in grouped:

        if pd.isna(peer_name):

            # Companies without peer group
            for _, row in peer_df.iterrows():

                _plot_chart(
                    company=row,
                    reference=nifty_avg,
                    reference_name="Nifty100 Avg",
                )

            continue

        peer_avg = peer_df[METRICS].mean()

        for _, row in peer_df.iterrows():
            
            print("Creating:", row["company_id"])

            _plot_chart(
                company=row,
                reference=peer_avg,
                reference_name="Peer Average",
            )


def _plot_chart(company, reference, reference_name):
    
    print("Saving chart:", company["company_id"])

    values = company[METRICS].fillna(0).tolist()
    ref = reference.fillna(0).tolist()

    n = len(METRICS)

    angles = np.linspace(
        0,
        2 * np.pi,
        n,
        endpoint=False,
    ).tolist()

    angles += angles[:1]

    values += values[:1]
    ref += ref[:1]

    fig = plt.figure(figsize=(7, 7))

    ax = plt.subplot(111, polar=True)

    ax.plot(
        angles,
        values,
        linewidth=2,
        label=company["company_id"],
    )

    ax.fill(
        angles,
        values,
        alpha=0.25,
    )

    ax.plot(
        angles,
        ref,
        linestyle="--",
        linewidth=2,
        label=reference_name,
    )

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(LABELS)

    ax.set_title(
        company["company_id"],
        fontsize=14,
        pad=20,
    )

    ax.legend(loc="upper right")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / f"{company['company_id']}_radar.png",
        dpi=300,
    )

    plt.close()