import datetime
from dataclasses import dataclass

from django.utils.timezone import make_aware, utc

from api.data import models as data_models


@dataclass
class Todo:
    description: str
    activate_date: str

    @classmethod
    def from_db(cls, instance: data_models.Todo) -> 'Todo':
        return cls(
            description=instance.description,
            activate_date=instance.activate_date.replace(microsecond=0, tzinfo=utc).strftime('%Y-%m-%dT%H:%M:%S')
        )

    def to_db(self) -> data_models.Todo:
        return data_models.Todo(
            description=self.description,
            activate_date=make_aware(
                datetime.datetime.strptime(self.activate_date, '%Y-%m-%dT%H:%M:%S'),
                utc
            )
        )


@dataclass
class Note:
    text: str
    position: int

    @classmethod
    def from_db(cls, instance: data_models.Note) -> 'Note':
        return cls(text=instance.text, position=instance.position)

    def to_db(self) -> data_models.Note:
        return data_models.Note(text=self.text, position=self.position)


@dataclass
class CodeSnippet:
    text: str
    position: int

    @classmethod
    def from_db(cls, instance: data_models.CodeSnippet) -> 'CodeSnippet':
        return cls(text=instance.text, position=instance.position)

    def to_db(self) -> data_models.CodeSnippet:
        return data_models.CodeSnippet(text=self.text, position=self.position)
