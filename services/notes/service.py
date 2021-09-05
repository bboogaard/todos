from typing import List

from django.core.cache import cache

from services.api import ItemApi
from services.notes.models import Note
from todos import models


class NoteService(ItemApi):

    _item_class = Note

    _model = models.Note

    _sort_attr = 'position'

    def save(self, items: List[str], **kwargs):
        index = kwargs.get('index', 0) or 0
        cache.set('notes-index', index)
        super().save(items)

    def get_index(self):
        return cache.get('notes-index', 0)

    def _from_items(self, items: List[str]) -> List[Note]:
        return list(map(lambda i: Note.from_item(i[1], position=i[0]), list(enumerate(items))))
