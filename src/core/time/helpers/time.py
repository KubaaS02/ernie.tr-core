from datetime import datetime, time, date


def month_days(month:date) -> int:
    m = month
    if m in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif m in [4, 6, 9, 11]:
        return 30
    else:
        return 28
