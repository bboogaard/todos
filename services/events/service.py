import calendar
from collections import defaultdict
from typing import List

from todos.models import Event
from services.api import EventsApi
from services.events.models import EventDate


class EventsService(EventsApi):

    def __init__(self):
        self.calendar = calendar.Calendar(firstweekday=6)

    def get_events(self, year: int, month: int) -> List[List[EventDate]]:
        events_in_db = defaultdict(list)
        for event_in_db in Event.objects.filter(date__year=year, date__month=month):
            events_in_db[event_in_db.date].append(event_in_db)

        events = []
        for week in self.calendar.monthdatescalendar(year, month):
            week_events = []
            for day in week:
                week_events.append(EventDate(date=day, events=list(map(str, events_in_db[day]))))
            events.append(week_events)
        return events
