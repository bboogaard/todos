from django.core.management.base import BaseCommand

from services.messages.factory import MessageServiceFactory
from services.todos.factory import TodosServiceFactory


class Command(BaseCommand):
    help = "Send upcoming todo's"

    def handle(self, *args, **kwargs):
        upcoming = TodosServiceFactory().create().upcoming()
        for todo in upcoming:
            print(todo)
            MessageServiceFactory().create().send(todo)
