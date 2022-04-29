import datetime
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from django.utils.html import mark_safe


@dataclass
class Date:
    date: date
    current_date_color: Optional[str] = ''

    def date_style(self):
        if self.date != datetime.date.today():
            return ''
        return mark_safe('color:{}'.format(self.current_date_color)) if self.current_date_color else ''


@dataclass
class Week:
    background: str
    color: str
    week_number: int
    dates: List[Date]

    def week_style(self):
        parts = []
        if self.background:
            parts.append('background-color:{}'.format(self.background))
        if self.color:
            parts.append('color:{}'.format(self.color))
        return mark_safe(";".join(parts))
