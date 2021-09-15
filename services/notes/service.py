import base64
from typing import List

from django.core.cache import cache
from django.db import transaction
from Crypto.Cipher import AES

from services.api import ItemApi
from services.notes.models import Note
from todos import models


class NoteService(ItemApi):

    _item_class = Note

    _model = models.Note

    _sort_attr = 'position'

    _separator = '\n----------\n'

    _iv = 16 * 'a'

    def save(self, items: List[str], **kwargs):
        index = kwargs.get('index', 0) or 0
        cache.set('notes-index', index)
        super().save(items)

    def get_index(self):
        return cache.get('notes-index', 0)

    @transaction.atomic()
    def encrypt(self, key: str):
        current = self._get_current()
        if not current:
            return
        print(current.position)

        obfuscated = AES.new(self._pad(key).encode(), AES.MODE_CBC, self._iv.encode()).encrypt(
            self._pad(current.text).encode())
        new_item = Note.from_item(base64.b64encode(obfuscated).decode(), position=current.position)
        new_item.to_db_item().save()
        models.Note.objects.filter(item_id=current.id).delete()

    def _from_items(self, items: List[str]) -> List[Note]:
        return list(map(lambda i: Note.from_item(i[1], position=i[0]), list(enumerate(items))))

    def _get_current(self):
        _persistent_items = self._get_persistent_items()
        try:
            return _persistent_items[self.get_index()]
        except IndexError:
            return None

    def _pad(self, value: str, pad_char: str = ' ') -> str:
        pad_length = 16 - divmod(len(value), 16)[1]
        return value + pad_length * pad_char
