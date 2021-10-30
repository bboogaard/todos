import calendar
from typing import List

from services.api import EventsApi
from services.events.models import EventDate


class EventsService(EventsApi):

    def __init__(self):
        self.calendar = calendar.Calendar(firstweekday=6)

    def get_events(self, year: int, month: int) -> List[List[EventDate]]:
        events = []
        for week in self.calendar.monthdatescalendar(year, month):
            week_events = []
            for day in week:
                week_events.append(EventDate(date=day))
            events.append(week_events)
        return events
