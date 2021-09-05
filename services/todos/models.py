import datetime
from dataclasses import dataclass
from typing import Optional

from services.models import PersistentItem
from todos import models


@dataclass
class Todo(PersistentItem):
    activated: Optional[datetime.datetime] = datetime.datetime.min

    @classmethod
    def from_db_item(cls, db_item: models.Todo) -> 'Todo':
        return cls(
            id=db_item.item_id,
            text=db_item.description,
            active=db_item.is_active,
            activated=db_item.activate_date
        )

    def to_db_item(self) -> models.Todo:
        return models.Todo(
            item_id=self.id,
            description=self.text,
            status=models.Todo.ACTIVE_STATUS if self.active else models.Todo.INACTIVE_STATUS
        )
