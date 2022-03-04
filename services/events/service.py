import calendar
import datetime
import operator
from collections import defaultdict
from typing import List, Tuple

from todos import models
from todos.settings import cache_settings
from services.api import EventsApi
from services.events.message_factory import EventMessageFactory
from services.events.models import Event, EventDate, WeekEvents
from services.messages.factory import MessageServiceFactory


class EventsService(EventsApi):

    def __init__(self):
        self.calendar = calendar.Calendar(firstweekday=6)
        settings = cache_settings.load()
        self.odd_weeks_background = settings.odd_weeks_background
        self.odd_weeks_color = settings.odd_weeks_color
        self.even_weeks_background = settings.even_weeks_background
        self.even_weeks_color = settings.even_weeks_color

    def get_events(self, year: int, month: int, start: datetime.date, end: datetime.date) -> \
            List[WeekEvents]:
        instances = list(models.Event.objects.filter(datetime__date__range=(start, end)))
        # + list(models.HistoricalDate.objects.for_date_range(start, end))
        events_in_db = defaultdict(list)
        for instance in instances:
            events_in_db[instance.event_date].append(Event.from_instance(instance))
        events = []
        for week in self.calendar.monthdatescalendar(year, month):
            dates = []
            week_number = week[0].isocalendar()[1]
            odd = bool(week_number % 2)
            for day in week:
                dates.append(
                    EventDate(
                        date=day,
                        events=list(sorted(events_in_db[(day.day, day.month)], key=operator.attrgetter('key')))
                    )
                )
            events.append(
                WeekEvents(
                    background=self.odd_weeks_background if odd else self.even_weeks_background,
                    color=self.odd_weeks_color if odd else self.even_weeks_color,
                    week_number=week_number,
                    dates=dates
                )
            )
        return events

    def send_upcoming_events(self):
        start = datetime.date.today()
        end = start + datetime.timedelta(days=7)
        queryset = models.Event.objects.filter(datetime__date__range=(start, end)).exclude(message_sent=True)
        events_in_db = defaultdict(list)
        for event in queryset:
            events_in_db[event.datetime_localized.date()].append(event)
        events = [
            EventDate(date=day, events=events)
            for day, events in events_in_db.items()
        ]
        if events:
            MessageServiceFactory.create().send(EventMessageFactory.create(events))
            queryset.update(message_sent=True)
