import datetime
import unittest.mock

import pytz
from constance.test import override_config
from django.conf import settings
from django.test.testcases import TestCase
from freezegun import freeze_time

from services.factory import EventsServiceFactory
from todos.models import Event
from tests.todos.factories import EventFactory, HistoricalDateFactory


@override_config(even_weeks_background='#FF3B0D', even_weeks_background_active=True,
                 even_weeks_color='#FFFFFF', even_weeks_color_active=True,
                 odd_weeks_current_date_color='#6C757D', odd_weeks_current_date_color_active=True)
class TestEventService(TestCase):

    def setUp(self):
        super().setUp()
        self.service = EventsServiceFactory.create()
        self.events = [
            EventFactory(
                description='Halloween',
                datetime=datetime.datetime(2021, 10, 31, 10, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
            ),
            EventFactory(
                description='Pay bills',
                datetime=datetime.datetime(2021, 11, 20, 10, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
            ),
            EventFactory(
                description='Take out trash',
                datetime=datetime.datetime(2021, 11, 20, 12, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
            ),
            EventFactory(
                description='Dentist',
                datetime=datetime.datetime(2021, 12, 1, 10, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
            )
        ]
        HistoricalDateFactory(
            date=datetime.date(1517, 10, 31),
            event="Luther's Ninety-five Theses posted"
        )
        HistoricalDateFactory(
            date=datetime.date(1941, 10, 31),
            event="Mount Rushmore Memorial finished"
        )

    @freeze_time('2021-10-31')
    def test_get_events(self):

        def _get_events(week_events):
            return [
                (event_date.date, ", ".join(map(str, event_date.events)))
                for event_date in week_events if event_date.events
            ]

        events = self.service.get_events(2021, 11, datetime.date(2021, 10, 1), datetime.date(2021, 12, 31))
        self.assertEqual(events[0].week_number, 43)
        self.assertEqual(events[0].week_style(), '')
        self.assertEqual(events[0].dates[0].date_style(), 'color:#6C757D')
        week1 = _get_events(events[0].dates)
        self.assertEqual(week1, [
            (datetime.date(2021, 10, 31),
             "Halloween")
            # "Halloween, Luther's Ninety-five Theses posted, Mount Rushmore Memorial finished")
        ])
        self.assertEqual(events[1].week_number, 44)
        self.assertEqual(events[1].week_style(), 'background-color:#FF3B0D;color:#FFFFFF')
        week2 = _get_events(events[1].dates)
        self.assertEqual(week2, [])
        self.assertEqual(events[2].week_number, 45)
        self.assertEqual(events[2].week_style(), '')
        week3 = _get_events(events[2].dates)
        self.assertEqual(week3, [(datetime.date(2021, 11, 20), "Pay bills, Take out trash")])
        self.assertEqual(events[3].week_number, 46)
        self.assertEqual(events[3].week_style(), 'background-color:#FF3B0D;color:#FFFFFF')
        week4 = _get_events(events[3].dates)
        self.assertEqual(week4, [])
        self.assertEqual(events[4].week_number, 47)
        self.assertEqual(events[4].week_style(), '')
        week5 = _get_events(events[4].dates)
        self.assertEqual(week5, [(datetime.date(2021, 12, 1), "Dentist")])

    @freeze_time('2021-11-18T12:00:00Z')
    def test_send_upcoming_events(self):
        with unittest.mock.patch('services.messages.service.MessageService.send') as mock_send:
            self.service.send_upcoming_events()
        event = Event.objects.get(pk=self.events[1].pk)
        self.assertTrue(event.message_sent)

        event = Event.objects.get(pk=self.events[2].pk)
        self.assertTrue(event.message_sent)

        message = mock_send.call_args[0][0]
        self.assertIn('Pay bills', message)
        self.assertIn('Take out trash', message)

        # Test that message_sent is updated
        with unittest.mock.patch('services.messages.service.MessageService.send') as mock_send:
            self.service.send_upcoming_events()

        self.assertFalse(mock_send.called)
