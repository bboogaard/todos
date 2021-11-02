import calendar
import datetime
from collections import defaultdict
from typing import Dict, List

from django.db.models import QuerySet

from todos.models import Event
from services.api import EventsApi
from services.events.message_factory import EventMessageFactory
from services.events.models import EventDate
from services.messages.factory import MessageServiceFactory


class EventsService(EventsApi):

    def __init__(self):
        self.calendar = calendar.Calendar(firstweekday=6)

    def get_events(self, year: int, month: int, start: datetime.date, end: datetime.date) -> List[List[EventDate]]:
        events_in_db = self._get_events_in_db(Event.objects.filter(date__range=(start, end)))
        events = []
        for week in self.calendar.monthdatescalendar(year, month):
            week_events = []
            for day in week:
                week_events.append(EventDate(date=day, events=list(map(str, events_in_db[day]))))
            events.append(week_events)
        return events

    def send_upcoming_events(self):
        start = datetime.date.today()
        end = start + datetime.timedelta(days=7)
        queryset = Event.objects.filter(date__range=(start, end)).exclude(message_sent=True)
        events_in_db = self._get_events_in_db(queryset)
        events = [
            EventDate(date=day, events=list(map(str, events)))
            for day, events in events_in_db.items()
        ]
        if events:
            MessageServiceFactory.create().send(EventMessageFactory.create(events))
            queryset.update(message_sent=True)

    @staticmethod
    def _get_events_in_db(queryset: QuerySet) -> Dict[datetime.date, List[Event]]:
        events_in_db = defaultdict(list)
        for event_in_db in queryset:
            events_in_db[event_in_db.date].append(event_in_db)
        return events_in_db
