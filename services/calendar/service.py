import calendar
from constance import config
from isoweek import Week as IsoWeek
from typing import List, Tuple

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

    def get_days(self, year: int, week: int) -> List[Date]:
        days = []
        week_obj = IsoWeek(year, week)
        odd = bool(week_obj.week % 2)
        for day in week_obj.days():
            days.append(
                Date(
                    date=day,
                    current_date_color=(
                        self.odd_weeks_current_date_color if odd else self.even_weeks_current_date_color),
                )
            )
        return days

    def get_prev_week(self, year: int, week: int) -> Tuple[int, int, int]:
        target_week, target_year = week - 1, year if week > 1 else (IsoWeek.last_week_of_year(year - 1).week, year - 1)
        week_obj = IsoWeek(target_year, target_week)
        return week_obj.day(0).year, week_obj.day(0).month, target_week

    def get_next_week(self, year: int, week: int) -> Tuple[int, int, int]:
        target_week, target_year = week + 1, year if week < IsoWeek.last_week_of_year(year).week else (1, year + 1)
        week_obj = IsoWeek(target_year, target_week)
        return week_obj.day(0).year, week_obj.day(0).month, target_week

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
