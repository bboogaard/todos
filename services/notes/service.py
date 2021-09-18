import base64
import binascii
from typing import List

from django.conf import settings
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

    def get_read_only(self) -> List[int]:
        items = self.get_active()
        read_only_items = self._to_items(list(self.filter(lambda t: t.active and t.is_encrypted)))
        return list(map(lambda i: items.index(i), read_only_items))

    @transaction.atomic()
    def encrypt(self, key: str):
        current = self._get_current()
        if not current:
            return

        try:
            base64.b64decode(current.text.encode())
            raise ValueError("Value already encoded")
        except binascii.Error:
            pass

        obfuscated = AES.new(
            self._pad(settings.SECRET_KEY, truncate=True).encode(),
            AES.MODE_CBC,
            self._iv.encode()
        ).encrypt(self._pad(current.text + ':' + key).encode())
        new_item = Note.from_item(
            base64.b64encode(obfuscated).decode(),
            position=current.position,
            is_encrypted=True
        )
        new_item.to_db_item().save()
        models.Note.objects.filter(item_id=current.id).delete()

    @transaction.atomic()
    def decrypt(self, key: str):
        current = self._get_current()
        if not current:
            return

        try:
            obfuscated = base64.b64decode(current.text.encode())
        except binascii.Error:
            raise ValueError("Value cannot be decoded")

        plain_text = AES.new(
            self._pad(settings.SECRET_KEY, truncate=True).encode(),
            AES.MODE_CBC,
            self._iv.encode()
        ).decrypt(obfuscated).decode()
        plain_text, control_key = plain_text.rstrip().rsplit(':', 1)
        if control_key != key:
            raise ValueError("Invalid key")

        new_item = Note.from_item(
            plain_text,
            position=current.position,
            is_encrypted=False
        )
        new_item.to_db_item().save()
        models.Note.objects.filter(item_id=current.id).delete()

    def _from_items(self, items: List[str]) -> List[Note]:
        return list(map(lambda i: Note.from_item(i[1], position=i[0]), list(enumerate(items))))

    def _get_current(self):
        try:
            return self.filter(lambda t: t.active)[self.get_index()]
        except IndexError:
            return None

    def _pad(self, value: str, pad_char: str = ' ', truncate: bool = False) -> str:
        pad_length = 16 - divmod(len(value), 16)[1]
        value = value + pad_length * pad_char
        return value[:16] if truncate else value
