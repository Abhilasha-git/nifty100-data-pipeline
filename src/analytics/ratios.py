def net_profit_margin(net_profit, sales):
    if sales == 0:
        return None

    return (net_profit / sales) * 100


def operating_profit_margin(operating_profit, sales):
    if sales == 0:
        return None

    return (operating_profit / sales) * 100


def opm_matches_source(
    operating_profit,
    sales,
    source_opm,
    tolerance=1
):
    calculated = operating_profit_margin(
        operating_profit,
        sales
    )

    if calculated is None:
        return True

    return abs(calculated - source_opm) <= tolerance


def return_on_equity(
    net_profit,
    equity,
    reserves
):
    capital = equity + reserves

    if capital <= 0:
        return None

    return (net_profit / capital) * 100


def return_on_capital_employed(
    operating_profit,
    other_income,
    equity,
    reserves,
    borrowings
):
    capital = equity + reserves + borrowings

    if capital <= 0:
        return None

    ebit = operating_profit + other_income

    return (ebit / capital) * 100


def return_on_assets(
    net_profit,
    total_assets
):
    if total_assets <= 0:
        return None

    return (net_profit / total_assets) * 100

def debt_to_equity(
    borrowings,
    equity,
    reserves
):
    capital = equity + reserves

    # Debt-free company
    if borrowings == 0:
        return 0

    # Negative or zero equity
    if capital <= 0:
        return None

    return borrowings / capital


def high_leverage_flag(
    debt_to_equity_ratio,
    is_financial=False
):
    if is_financial:
        return False

    if debt_to_equity_ratio is None:
        return False

    return debt_to_equity_ratio > 5


def interest_coverage(
    operating_profit,
    other_income,
    interest
):
    if interest == 0:
        return None

    ebit = operating_profit + other_income

    return ebit / interest


def icr_label(
    interest
):
    if interest == 0:
        return "Debt Free"

    return ""


def interest_coverage_warning(
    interest_coverage_ratio
):
    if interest_coverage_ratio is None:
        return False

    return interest_coverage_ratio < 1.5


def net_debt(
    borrowings,
    investments
):
    return borrowings - investments


def asset_turnover(
    sales,
    total_assets
):
    if total_assets == 0:
        return None

    return sales / total_assets