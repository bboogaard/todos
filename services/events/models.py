from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from django.utils.html import mark_safe

from todos import models


@dataclass
class Event:
    instance: models.EventMixin
    type: str

    def __str__(self):
        return str(self.instance)

    @classmethod
    def from_instance(cls, instance: models.EventMixin) -> 'Event':
        if isinstance(instance, models.Event):
            event_type = 'event'
        elif isinstance(instance, models.HistoricalDate):
            event_type = 'hist_date'
        else:
            raise NotImplementedError()

        return cls(instance=instance, type=event_type)

    @property
    def key(self):
        return self.type, self.instance.event_key


@dataclass
class EventDate:
    date: date
    events: Optional[List[Event]] = field(default_factory=lambda: [])


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
