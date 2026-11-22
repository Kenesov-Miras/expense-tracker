from datetime import datetime


def filter_month(expenses, month):
    """Return expenses whose date falls in month (YYYY-MM)."""
    result = []
    for e in expenses:
        d = datetime.strptime(e.date, "%Y-%m-%d")
        if d.strftime("%Y-%m") == month:
            result.append(e)
    return result


def totals_by_category(expenses):
    totals = {}
    for e in expenses:
        totals[e.category] = totals.get(e.category, 0) + e.amount
    return totals


def grand_total(expenses):
    total = 0
    for e in expenses:
        total += e.amount
    return total
