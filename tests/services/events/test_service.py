import datetime
import unittest.mock

import pytz
from django.conf import settings
from django.test.testcases import TestCase
from freezegun import freeze_time

from services.factory import EventsServiceFactory
from todos.models import Event
from tests.todos.factories import EventFactory


class TestEventService(TestCase):

    def setUp(self):
        super().setUp()
        self.service = EventsServiceFactory.create()
        self.events = [
            EventFactory(
                description='Halloween',
                datetime=datetime.datetime(2020, 10, 31, 10, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
            ),
            EventFactory(
                description='Pay bills',
                datetime=datetime.datetime(2020, 11, 20, 10, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
            ),
            EventFactory(
                description='Take out trash',
                datetime=datetime.datetime(2020, 11, 20, 12, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
            ),
            EventFactory(
                description='Dentist',
                datetime=datetime.datetime(2020, 12, 1, 10, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
            )
        ]

    def test_get_events(self):

        def _get_events(week_events):
            return [(event_date.date, ", ".join(map(str, event_date.events))) for event_date in week_events if event_date.events]

        events = self.service.get_events(2020, 11, datetime.date(2020, 10, 1), datetime.date(2020, 12, 31))
        week1 = _get_events(events[0])
        self.assertEqual(week1, [])
        week2 = _get_events(events[1])
        self.assertEqual(week2, [])
        week3 = _get_events(events[2])
        self.assertEqual(week3, [(datetime.date(2020, 11, 20), "Pay bills, Take out trash")])
        week4 = _get_events(events[3])
        self.assertEqual(week4, [])
        week5 = _get_events(events[4])
        self.assertEqual(week5, [(datetime.date(2020, 12, 1), "Dentist")])

    @freeze_time('2020-11-18T12:00:00Z')
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
