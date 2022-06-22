import datetime

from constance.test import override_config
from django.test.testcases import TestCase
from freezegun import freeze_time

from services.factory import CalendarServiceFactory


@override_config(even_weeks_background='#FF3B0D', even_weeks_background_active=True,
                 even_weeks_color='#FFFFFF', even_weeks_color_active=True,
                 odd_weeks_current_date_color='#6C757D', odd_weeks_current_date_color_active=True)
class TestEventService(TestCase):

    def setUp(self):
        super().setUp()
        self.service = CalendarServiceFactory.create()

    @freeze_time('2021-01-04')
    def test_get_days(self):
        days = self.service.get_days(2021, 1)
        self.assertEqual(days[0].date, datetime.date(2021, 1, 4))
        self.assertEqual(days[0].date_style(), 'color:#6C757D')
        self.assertEqual(days[1].date, datetime.date(2021, 1, 5))
        self.assertEqual(days[1].date_style(), '')
        self.assertEqual(days[2].date, datetime.date(2021, 1, 6))
        self.assertEqual(days[2].date_style(), '')
        self.assertEqual(days[3].date, datetime.date(2021, 1, 7))
        self.assertEqual(days[3].date_style(), '')
        self.assertEqual(days[4].date, datetime.date(2021, 1, 8))
        self.assertEqual(days[4].date_style(), '')
        self.assertEqual(days[5].date, datetime.date(2021, 1, 9))
        self.assertEqual(days[5].date_style(), '')
        self.assertEqual(days[6].date, datetime.date(2021, 1, 10))
        self.assertEqual(days[6].date_style(), '')

    def test_get_prev_week(self):
        year, month, week = self.service.get_prev_week(2021, 1)
        self.assertEqual(year, 2020)
        self.assertEqual(month, 12)
        self.assertEqual(week, 53)

    def test_get_next_week(self):
        year, month, week = self.service.get_next_week(2021, 1)
        self.assertEqual(year, 2021)
        self.assertEqual(month, 1)
        self.assertEqual(week, 2)

    @freeze_time('2020-12-28')
    def test_get_weeks(self):
        weeks = self.service.get_weeks(2021, 1)
        self.assertEqual(weeks[0].week_number, 53)
        self.assertEqual(weeks[0].week_style(), '')
        self.assertEqual(weeks[0].dates[0].date_style(), 'color:#6C757D')
        self.assertEqual(weeks[1].week_number, 1)
        self.assertEqual(weeks[1].week_style(), '')
        self.assertEqual(weeks[2].week_number, 2)
        self.assertEqual(weeks[2].week_style(), 'background-color:#FF3B0D;color:#FFFFFF')
        self.assertEqual(weeks[3].week_number, 3)
        self.assertEqual(weeks[3].week_style(), '')
        self.assertEqual(weeks[4].week_number, 4)
        self.assertEqual(weeks[4].week_style(), 'background-color:#FF3B0D;color:#FFFFFF')
        self.assertEqual(weeks[5].week_number, 5)
        self.assertEqual(weeks[5].week_style(), '')
