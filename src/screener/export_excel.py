from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter
import pandas as pd


GREEN = PatternFill(
    fill_type="solid",
    start_color="C6EFCE",
)

RED = PatternFill(
    fill_type="solid",
    start_color="FFC7CE",
)


COLUMN_MAP = {
    "roe_min": "return_on_equity_pct",
    "debt_to_equity_max": "debt_to_equity",
    "free_cash_flow_min": "free_cash_flow_cr",
    "revenue_cagr_5yr_min": "revenue_cagr_5yr",
    "pat_cagr_5yr_min": "pat_cagr_5yr",
    "eps_cagr_5yr_min": "eps_cagr_5yr",
    "opm_min": "operating_profit_margin_pct",
    "interest_coverage_min": "interest_coverage",
    "asset_turnover_min": "asset_turnover",
    "sales_min": "sales",
    "net_profit_min": "net_profit",
}


KPI_COLUMNS = [
    "company_id",
    "company_name",
    "broad_sector",
    "sub_sector",
    "market_cap_category",
    "year",
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "free_cash_flow_cr",
    "cfo_pat_ratio",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "sales",
    "net_profit",
    "composite_quality_score",
    "sector_quality_score",
]


def export_screener_results(
    results,
    config,
    output_file="output/screener_output.xlsx",
):
    """
    Export screener results to Excel.
    """

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl",
    ) as writer:

        for preset_name, df in results.items():

            preset = config[preset_name]

            sheet_df = df.copy()

            cols = [
                c for c in KPI_COLUMNS
                if c in sheet_df.columns
            ]

            sheet_df = (
                sheet_df[cols]
                .sort_values(
                    "composite_quality_score",
                    ascending=False,
                )
            )

            sheet_df.to_excel(
                writer,
                sheet_name=preset_name[:31],
                index=False,
            )

            ws = writer.sheets[preset_name[:31]]

            ws.freeze_panes = "A2"

            headers = {
                cell.value: cell.column
                for cell in ws[1]
            }

            for metric, threshold in preset.items():

                if metric not in COLUMN_MAP:
                    continue

                column_name = COLUMN_MAP[metric]

                if column_name not in headers:
                    continue

                col = headers[column_name]

                for row in range(2, ws.max_row + 1):

                    cell = ws.cell(row=row, column=col)

                    if cell.value is None:
                        continue

                    if metric.endswith("_max"):

                        if cell.value <= threshold:
                            cell.fill = GREEN
                        else:
                            cell.fill = RED

                    else:

                        if cell.value >= threshold:
                            cell.fill = GREEN
                        else:
                            cell.fill = RED

            for column_cells in ws.columns:

                width = max(
                    len(str(cell.value))
                    if cell.value is not None else 0
                    for cell in column_cells
                )

                ws.column_dimensions[
                    get_column_letter(column_cells[0].column)
                ].width = min(width + 2, 30)

    print(f"\nSaved: {output_file}")