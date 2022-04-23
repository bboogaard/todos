import datetime
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from django.utils.html import mark_safe

from api.views.internal.models import Event


@dataclass
class EventDate:
    date: date
    current_date_color: Optional[str] = ''
    events: Optional[List[Event]] = field(default_factory=lambda: [])

    def date_style(self):
        if self.date != datetime.date.today():
            return ''
        return mark_safe('color:{}'.format(self.current_date_color)) if self.current_date_color else ''


@dataclass
class WeekEvents:
    background: str
    color: str
    week_number: int
    dates: List[EventDate]

    def week_style(self):
        parts = []
        if self.background:
            parts.append('background-color:{}'.format(self.background))
        if self.color:
            parts.append('color:{}'.format(self.color))
        return mark_safe(";".join(parts))
