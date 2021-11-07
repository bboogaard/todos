from django.core.management.base import BaseCommand

from services.factory import EventsServiceFactory


class Command(BaseCommand):
    help = "Send upcoming events"

    def handle(self, *args, **kwargs):
        EventsServiceFactory.create().send_upcoming_events()
