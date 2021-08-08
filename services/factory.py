from services.notes.service import NoteService
from services.todos.service import TodoService


class ItemServiceFactory:

    @classmethod
    def todos(cls):
        return TodoService()

    @classmethod
    def notes(cls):
        return NoteService()
