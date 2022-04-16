import json
from abc import ABC
from io import BytesIO
from typing import IO, List, Type

from dacite import from_dict
from dataclasses import asdict, dataclass
from django.db.models import Model


class ExportApi(ABC):

    item_class: Type[dataclass]

    model_class: Type[Model]

    separator: str = '\n'

    def dump(self) -> IO[bytes]:
        items = self.get_items()
        return BytesIO(self.separator.join(items).encode())

    def load(self, file: IO[bytes]):
        items = file.read().decode().split(self.separator)
        self.save_items(items)

    def get_items(self) -> List[str]:
        instances = self.get_queryset()
        items = [self.item_class.from_db(instance) for instance in instances]
        return [json.dumps(asdict(item)) for item in items]

    def save_items(self, items: List[str]):
        items = [from_dict(self.item_class, json.loads(item)) for item in items]
        for item in items:
            instance = item.to_db()
            instance.save()

    def get_queryset(self):
        return self.model_class.objects.all()
