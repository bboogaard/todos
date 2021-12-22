from typing import List

from django.core.cache import cache

from services.api import ItemApi
from services.notes.models import Note
from todos import models


class NoteService(ItemApi):

    _item_class = Note

    _model = models.Note

    _sort_attr = 'position'

    _separator = '\n----------\n'

    def search(self, search_query: str) -> List[str]:
        if not search_query:
            return []

        return self._to_items(
            list(filter(lambda t: t.active and search_query == t.id, self.persistent_items))
        )

    def save(self, items: List[str], is_filtered: bool = False, **kwargs):
        index = kwargs.get('index', 0) or 0
        cache.set('notes-index', index)
        super().save(items, is_filtered)

    def get_index(self):
        return cache.get('notes-index', 0)

    def _from_items(self, items: List[str]) -> List[Note]:
        return list(map(lambda i: Note.from_item(i[1], position=i[0]), list(enumerate(items))))
