import operator
import re
from abc import ABC
from datetime import date
from typing import List

from django.core.cache import cache
from django.db import transaction
from django.utils.text import slugify

from services.todos.models import Todo
from todos import models


re_date = re.compile(r'(\d{2})-(\d{2})-(\d{4})')


class TodoService(ABC):

    _todos: List[Todo] = None

    @property
    def todos(self):
        if self._todos is None:
            self._todos = self._get_todos()

        return self._todos

    def all(self) -> List[str]:
        return self._to_items(self.todos)

    def get_active(self) -> List[str]:
        return self._to_items(list(filter(lambda t: t.active, self.todos)))

    def search(self, search_query: str) -> List[str]:
        if not search_query:
            return []

        return self._to_items(
            list(filter(lambda t: not t.active and search_query.upper() in t.text.upper(), self.todos))
        )

    def upcoming(self) -> List[str]:
        dated_items = list(
            filter(lambda x: x[0].active and x[1], map(lambda t: (t, re_date.search(t.text)), self.todos))
        )
        today = date.today()
        upcoming = []
        for todo, match in dated_items:
            cache_key = self._make_cache_key(todo.text, 'sent')
            sent = cache.get(cache_key)
            if sent:
                continue
            dt = date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
            if 0 < (dt - today).days < 7:
                upcoming.append(todo)
                cache.set(cache_key, '1')
        return self._to_items(upcoming)

    @transaction.atomic()
    def save(self, items: List[str]):
        _todos = self._get_todos()
        todos = self._from_items(items)
        for todo in todos:
            todo_in_db = next(filter(lambda t: t.id == todo.id, _todos), None)
            if todo_in_db is None:
                _todos.append(todo)
            elif not todo_in_db.active:
                todo_in_db.active = True
        for todo_in_db in _todos:
            todo = next(filter(lambda t: t.id == todo_in_db.id, todos), None)
            if todo is None:
                todo_in_db.active = False

        todos_in_db = models.Todo.objects.in_bulk(field_name='todo_id')
        for todo in _todos:
            todo_to_update = todos_in_db.get(todo.id)
            if todo_to_update is not None and todo_to_update.is_active != todo.active:
                func = 'activate' if todo.active else 'soft_delete'
                getattr(todo_to_update, func)()
            elif todo_to_update is None:
                todo_to_create = todo.to_todo()
                todo_to_create.save()

    @transaction.atomic()
    def activate(self, items: List[str]):
        _todos = self._get_todos()
        todos = self._from_items(items)
        for todo in todos:
            todo_in_db = next(filter(lambda t: t.id == todo.id, _todos), None)
            if todo_in_db is not None:
                todo_in_db.active = True

        todos_in_db = models.Todo.objects.in_bulk(field_name='todo_id')
        for todo in filter(lambda t: t.active, _todos):
            todo_to_update = todos_in_db.get(todo.id)
            if todo_to_update is not None and not todo_to_update.is_active:
                todo_to_update.activate()

    @staticmethod
    def _get_todos() -> List[Todo]:
        queryset = models.Todo.objects.get_queryset()
        return list(map(lambda t: Todo.from_todo(t), list(queryset)))

    @staticmethod
    def _to_items(todos: List[Todo], sort_attr: str = 'activated') -> List[str]:
        return list(map(lambda t: t.text, sorted(todos, key=operator.attrgetter(sort_attr))))

    @staticmethod
    def _from_items(items: List[str]) -> List[Todo]:
        return list(map(lambda i: Todo.from_item(i), items))

    @staticmethod
    def _make_cache_key(text: str, action: str) -> str:
        return slugify('{}-{}'.format(text, action))
