from datetime import datetime, time, date
from calendar import monthrange
from typing import Tuple
def month_days(month:date) -> Tuple[int, int]:
    return monthrange(month.year, month.month)[1]
