from services.events.service import EventsService


class EventsServiceFactory:

    @classmethod
    def create(cls):
        return EventsService()
