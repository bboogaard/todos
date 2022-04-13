from dataclasses import dataclass

from api.data import models as data_models


@dataclass
class Todo:
    description: str

    @classmethod
    def from_db(cls, instance: data_models.Todo) -> 'Todo':
        return cls(description=instance.description)

    def to_db(self) -> data_models.Todo:
        return data_models.Todo(description=self.description)
