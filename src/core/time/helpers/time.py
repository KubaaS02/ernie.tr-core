from datetime import date
from calendar import monthrange


def month_days(month: date) -> int:
    return monthrange(month.year, month.month)[1]
