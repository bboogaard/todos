import operator
from abc import ABC
from io import BytesIO
from typing import IO, List, Type

from django.db import transaction

from .models import PersistentItem
from todos import models


class Api(ABC):

    def dump(self, filename: str) -> IO[bytes]:
        raise NotImplementedError()

    def load(self, file: IO[bytes]):
        raise NotImplementedError()


class ItemApi(Api):

    _item_class: Type[PersistentItem]

    _persistent_items: List[PersistentItem] = None

    _model: Type[models.Item]

    _sort_attr: str

    _separator: str

    @property
    def persistent_items(self):
        if self._persistent_items is None:
            self._persistent_items = self._get_persistent_items()

        return self._persistent_items

    def all(self) -> List[str]:
        return self._to_items(self.persistent_items)

    def get_active(self) -> List[str]:
        return self._to_items(list(filter(lambda t: t.active, self.persistent_items)))

    def search(self, search_query: str) -> List[str]:
        if not search_query:
            return []

        return self._to_items(
            list(filter(lambda t: not t.active and search_query.upper() in t.text.upper(), self.persistent_items))
        )

    @transaction.atomic()
    def save(self, items: List[str], **kwargs):
        _persistent_items = self._get_persistent_items()
        items = self._from_items(items)
        for item in items:
            item_in_db = next(filter(lambda t: t.id == item.id, _persistent_items), None)
            if item_in_db is None:
                _persistent_items.append(item)
            elif not item_in_db.active:
                item_in_db.active = True
        for item_in_db in _persistent_items:
            item = next(filter(lambda t: t.id == item_in_db.id, items), None)
            if item is None:
                item_in_db.active = False

        items_in_db = self._model.objects.in_bulk(field_name='item_id')
        for item in _persistent_items:
            item_to_update = items_in_db.get(item.id)
            if item_to_update is not None and item_to_update.is_active != item.active:
                func = 'activate' if item.active else 'soft_delete'
                getattr(item_to_update, func)()
            elif item_to_update is None:
                item_to_create = item.to_db_item()
                item_to_create.save()

    @transaction.atomic()
    def activate(self, items: List[str]):
        _persistent_items = self._get_persistent_items()
        items = self._from_items(items)
        for item in items:
            item_in_db = next(filter(lambda t: t.id == item.id, _persistent_items), None)
            if item_in_db is not None:
                item_in_db.active = True

        items_in_db = self._model.objects.in_bulk(field_name='item_id')
        for item in filter(lambda t: t.active, _persistent_items):
            item_to_update = items_in_db.get(item.id)
            if item_to_update is not None and not item_to_update.is_active:
                item_to_update.activate()

    def dump(self, filename: str) -> IO[bytes]:
        items = self.get_active()
        return BytesIO(self._separator.join(items).encode())

    def load(self, file: IO[bytes]):
        items = file.read().decode().split(self._separator)
        self.save(items)

    def _get_persistent_items(self) -> List[PersistentItem]:
        queryset = self._model.objects.get_queryset()
        return list(map(lambda t: self._item_class.from_db_item(t), list(queryset)))

    def _to_items(self, persistent_items: List[PersistentItem]) -> List[str]:
        return list(map(lambda t: t.text, sorted(persistent_items, key=operator.attrgetter(self._sort_attr))))

    def _from_items(self, items: List[str]) -> List[PersistentItem]:
        return list(map(lambda i: self._item_class.from_item(i), items))


class FilesApi(ABC):
    pass


class EventsApi(ABC):
    pass
