import hashlib
from dataclasses import dataclass

from todos.models import Item


@dataclass
class PersistentItem:
    id: str
    text: str
    active: bool

    @classmethod
    def from_item(cls, item: str, **kwargs):
        return cls(
            id=hashlib.md5(item.encode()).hexdigest(),
            text=item,
            active=True
        )

    @classmethod
    def from_db_item(cls, db_item: Item) -> 'PersistentItem':
        raise NotImplementedError()

    def to_db_item(self) -> Item:
        raise NotImplementedError()
