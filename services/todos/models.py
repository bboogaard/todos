import datetime
import hashlib
from dataclasses import dataclass
from typing import Optional

from todos import models


@dataclass
class Todo:
    id: str
    text: str
    active: bool
    activated: Optional[datetime.datetime] = datetime.datetime.min

    @classmethod
    def from_item(cls, item: str) -> 'Todo':
        return cls(
            id=hashlib.md5(item.encode()).hexdigest(),
            text=item,
            active=True
        )

    @classmethod
    def from_todo(cls, todo: models.Todo) -> 'Todo':
        return cls(
            id=todo.todo_id,
            text=todo.description,
            active=todo.is_active,
            activated=todo.activate_date
        )

    def to_todo(self) -> models.Todo:
        return models.Todo(
            todo_id=self.id,
            description=self.text,
            status=models.Todo.ACTIVE_STATUS if self.active else models.Todo.INACTIVE_STATUS
        )
