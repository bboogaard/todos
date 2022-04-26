import calendar
from constance import config
from typing import List

from services.api import CalendarApi
from services.calendar.models import Date, Week


class CalendarService(CalendarApi):

    def __init__(self):
        self.calendar = calendar.Calendar(firstweekday=6)
        self.odd_weeks_background = config.odd_weeks_background if config.odd_weeks_background_active else ''
        self.odd_weeks_color = config.odd_weeks_color if config.odd_weeks_color_active else ''
        self.odd_weeks_current_date_color = config.odd_weeks_current_date_color if \
            config.odd_weeks_current_date_color_active else ''
        self.even_weeks_background = config.even_weeks_background if config.even_weeks_background_active else ''
        self.even_weeks_color = config.even_weeks_color if config.even_weeks_color_active else ''
        self.even_weeks_current_date_color = config.even_weeks_current_date_color if \
            config.even_weeks_current_date_color_active else ''

    def get_weeks(self, year: int, month: int) -> List[Week]:
        weeks = []
        for week in self.calendar.monthdatescalendar(year, month):
            dates = []
            week_number = week[0].isocalendar()[1]
            odd = bool(week_number % 2)
            for day in week:
                dates.append(
                    Date(
                        date=day,
                        current_date_color=(
                            self.odd_weeks_current_date_color if odd else self.even_weeks_current_date_color),
                    )
                )
            weeks.append(
                Week(
                    background=self.odd_weeks_background if odd else self.even_weeks_background,
                    color=self.odd_weeks_color if odd else self.even_weeks_color,
                    week_number=week_number,
                    dates=dates
                )
            )
        return weeks
