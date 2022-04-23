import datetime
from typing import List, Optional

import pytz
from django.conf import settings
from django.utils.timezone import make_aware


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


def to_date(date_str: str, date_format: str = '%Y-%m-%d') -> Optional[datetime.date]:
    try:
        return datetime.datetime.strptime(date_str, date_format).date()
    except ValueError:
        return None


def day_start(date: datetime.date, time_zone: str = '') -> datetime.datetime:
    dt = datetime.datetime.combine(date, datetime.time(0, 0, 0))
    return make_aware(dt, pytz.timezone(time_zone or settings.TIME_ZONE))


def day_end(date: datetime.date, time_zone: str = '') -> datetime.datetime:
    dt = datetime.datetime.combine(date, datetime.time(23, 59, 59))
    return make_aware(dt, pytz.timezone(time_zone or settings.TIME_ZONE))
