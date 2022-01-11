import datetime
from typing import List


MONTH_NAMES = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
]


def date_range(start: datetime.date, end: datetime.date) -> List[datetime.date]:
    delta = end - start
    return [start + datetime.timedelta(days=i) for i in range(delta.days + 1)]
