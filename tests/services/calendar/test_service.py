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

    @freeze_time('2021-10-31')
    def test_get_weeks(self):
        weeks = self.service.get_weeks(2021, 11)
        self.assertEqual(weeks[0].week_number, 43)
        self.assertEqual(weeks[0].week_style(), '')
        self.assertEqual(weeks[0].dates[0].date_style(), 'color:#6C757D')
        self.assertEqual(weeks[1].week_number, 44)
        self.assertEqual(weeks[1].week_style(), 'background-color:#FF3B0D;color:#FFFFFF')
        self.assertEqual(weeks[2].week_number, 45)
        self.assertEqual(weeks[2].week_style(), '')
        self.assertEqual(weeks[3].week_number, 46)
        self.assertEqual(weeks[3].week_style(), 'background-color:#FF3B0D;color:#FFFFFF')
        self.assertEqual(weeks[4].week_number, 47)
        self.assertEqual(weeks[4].week_style(), '')
