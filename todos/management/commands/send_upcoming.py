import sys

from django.core.management.base import BaseCommand

from services.factory import ItemServiceFactory
from services.messages.factory import MessageServiceFactory


class Command(BaseCommand):
    help = "Send upcoming todo's"

    def handle(self, *args, **kwargs):
        upcoming = ItemServiceFactory().todos().upcoming()
        for todo in upcoming:
            sys.stdout.write('Sending {}\n'.format(todo))
            MessageServiceFactory().create().send(todo)
