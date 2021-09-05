import re
from datetime import date
from typing import List

from django.core.cache import cache
from django.utils.text import slugify

from services.api import ItemApi
from services.todos.models import Todo
from todos import models


re_date = re.compile(r'(\d{2})-(\d{2})-(\d{4})')


class TodoService(ItemApi):

    _item_class = Todo

    _model = models.Todo

    _sort_attr = 'activated'

    def upcoming(self) -> List[str]:
        dated_items = list(
            filter(lambda x: x[0].active and x[1], map(lambda t: (t, re_date.search(t.text)), self.persistent_items))
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

    @staticmethod
    def _make_cache_key(text: str, action: str) -> str:
        return slugify('{}-{}'.format(text, action))
