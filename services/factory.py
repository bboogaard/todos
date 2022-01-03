from services.events.service import EventsService
from services.files.service import FilesService, ImagesService
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
    def create(cls, file_type: str = 'file'):
        return FilesService() if file_type == 'file' else ImagesService()


class EventsServiceFactory:

    @classmethod
    def create(cls):
        return EventsService()
