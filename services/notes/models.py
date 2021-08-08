from dataclasses import dataclass, field

from services.models import PersistentItem
from todos import models


@dataclass
class Note(PersistentItem):
    position: int = field(init=False, default=0)

    @classmethod
    def from_item(cls, item: str, **kwargs):
        note = super().from_item(item)
        note.position = kwargs.get('position', 0) or 0
        return note

    @classmethod
    def from_db_item(cls, db_item: models.Note) -> 'Note':
        note = cls(
            id=db_item.item_id,
            text=db_item.text,
            active=db_item.is_active
        )
        note.position = db_item.position
        return note

    def to_db_item(self) -> models.Note:
        return models.Note(
            item_id=self.id,
            text=self.text,
            status=models.Note.ACTIVE_STATUS if self.active else models.Note.INACTIVE_STATUS,
            position=self.position
        )
