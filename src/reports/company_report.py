from pathlib import Path

OUTPUT_DIR = Path("reports/company_reports")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for _, row in df.iterrows():

    html = f"""
    <html>
    <head>
        <title>{row['company_name']}</title>
    </head>

    <body>

    <h1>{row['company_name']}</h1>

    <p><b>Company ID:</b> {row['company_id']}</p>

    <p><b>Sector:</b> {row['broad_sector']}</p>

    <p><b>Composite Score:</b> {row['composite_quality_score']:.2f}</p>

    <img src="../radar_charts/{row['company_id']}_radar.png" width="600">

    </body>
    </html>
    """

    with open(
        OUTPUT_DIR / f"{row['company_id']}.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)
        
        generate_radar_charts(df)
        generate_all_reports(df)