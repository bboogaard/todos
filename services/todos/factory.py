from services.todos.service import TodoService


class TodosServiceFactory:

    @classmethod
    def create(cls):
        return TodoService()
