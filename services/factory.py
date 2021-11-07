from services.events.service import EventsService
from services.files.service import FilesService
from services.notes.service import NoteService
from services.todos.service import TodoService


class ItemServiceFactory:

    @classmethod
    def todos(cls):
        return TodoService()

    @classmethod
    def notes(cls):
        return NoteService()


class FilesServiceFactory:

    @classmethod
    def create(cls):
        return FilesService()


class EventsServiceFactory:

    @classmethod
    def create(cls):
        return EventsService()
