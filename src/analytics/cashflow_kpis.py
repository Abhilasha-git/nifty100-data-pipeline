def free_cash_flow(
    operating_activity,
    investing_activity
):
    """
    FCF = CFO + CFI
    """
    return operating_activity + investing_activity


def cfo_quality_score(
    operating_cash_flow,
    net_profit
):
    """
    Returns:
        ("High Quality", ratio)
        ("Moderate", ratio)
        ("Accrual Risk", ratio)
        (None, None)
    """

    if net_profit == 0:
        return None, None

    ratio = operating_cash_flow / net_profit

    if ratio > 1:
        label = "High Quality"
    elif ratio >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"

    return label, ratio


def capex_intensity(
    investing_activity,
    sales
):
    """
    CapEx / Sales %
    """

    if sales == 0:
        return None, None

    pct = abs(investing_activity) / sales * 100

    if pct < 3:
        label = "Asset Light"
    elif pct <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"

    return label, pct


def fcf_conversion_rate(
    free_cash_flow,
    operating_profit
):
    if operating_profit == 0:
        return None

    return (free_cash_flow / operating_profit) * 100


def capital_allocation_pattern(
    cfo,
    cfi,
    cff,
    cfo_quality=None
):
    """
    Returns one of the 8 Sprint labels.
    """

    signs = (
        "+" if cfo >= 0 else "-",
        "+" if cfi >= 0 else "-",
        "+" if cff >= 0 else "-"
    )

    if signs == ("+", "-", "-"):
        if cfo_quality == "High Quality":
            return "Shareholder Returns"
        return "Reinvestor"

    if signs == ("+", "+", "-"):
        return "Liquidating Assets"

    if signs == ("-", "+", "+"):
        return "Distress Signal"

    if signs == ("-", "-", "+"):
        return "Growth Funded by Debt"

    if signs == ("+", "+", "+"):
        return "Cash Accumulator"

    if signs == ("-", "-", "-"):
        return "Pre-Revenue"

    if signs == ("+", "-", "+"):
        return "Mixed"

    return "Unknown"

def cfo_quality_score(cfo_values, pat_values):
    """
    Average CFO/PAT ratio over available years.

    Returns:
        (average_ratio, quality_label)
    """

    ratios = []

    for cfo, pat in zip(cfo_values, pat_values):

        if pat == 0:
            continue

        ratios.append(cfo / pat)

    if not ratios:
        return None, None

    average = sum(ratios) / len(ratios)

    if average > 1.0:
        label = "High Quality"

    elif average >= 0.5:
        label = "Moderate"

    else:
        label = "Accrual Risk"

    return average, label

def capital_allocation_pattern(
    operating_activity,
    investing_activity,
    financing_activity,
    cfo_pat_ratio=None
):
    """
    Classify capital allocation pattern based on
    CFO, CFI and CFF signs.
    """

    cfo = "+" if operating_activity >= 0 else "-"
    cfi = "+" if investing_activity >= 0 else "-"
    cff = "+" if financing_activity >= 0 else "-"

    pattern = (cfo, cfi, cff)

    if pattern == ("+", "-", "-"):
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1:
            return "Shareholder Returns"
        return "Reinvestor"

    if pattern == ("+", "+", "-"):
        return "Liquidating Assets"

    if pattern == ("-", "+", "+"):
        return "Distress Signal"

    if pattern == ("-", "-", "+"):
        return "Growth Funded by Debt"

    if pattern == ("+", "+", "+"):
        return "Cash Accumulator"

    if pattern == ("-", "-", "-"):
        return "Pre-Revenue"

    if pattern == ("+", "-", "+"):
        return "Mixed"

    return "Other"