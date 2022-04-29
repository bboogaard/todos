from services.calendar.service import CalendarService


class CalendarServiceFactory:

    @classmethod
    def create(cls):
        return CalendarService()
