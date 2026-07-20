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
    if total_assets == 0:
        return None

    return (net_profit / total_assets) * 100