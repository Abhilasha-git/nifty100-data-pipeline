def cagr(start_value, end_value, years):
    """
    Calculate CAGR and return (value, flag).

    Flags:
    None                -> valid CAGR
    ZERO_BASE           -> start value is zero
    TURNAROUND          -> negative to positive
    DECLINE_TO_LOSS     -> positive to negative
    BOTH_NEGATIVE       -> both negative
    INSUFFICIENT        -> less than required years
    """

    if years <= 0:
        return None, "INSUFFICIENT"

    if start_value == 0:
        return None, "ZERO_BASE"

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    value = ((end_value / start_value) ** (1 / years) - 1) * 100

    return value, None


def revenue_cagr(start_sales, end_sales, years):
    return cagr(start_sales, end_sales, years)


def pat_cagr(start_profit, end_profit, years):
    return cagr(start_profit, end_profit, years)


def eps_cagr(start_eps, end_eps, years):
    return cagr(start_eps, end_eps, years)