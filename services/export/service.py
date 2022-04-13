import json
from typing import List

from dacite import from_dict
from dataclasses import asdict
from services.export.api import ExportApi

from api.data import models as data_models
from services.export.models import Todo


class TodoExportService(ExportApi):

    def get_items(self) -> List[str]:
        instances = data_models.Todo.objects.active()
        todos = [Todo.from_db(instance) for instance in instances]
        return [json.dumps(asdict(todo)) for todo in todos]

    def save_items(self, items: List[str]):
        todos = [from_dict(Todo, json.loads(item)) for item in items]
        for todo in todos:
            instance = todo.to_db()
            instance.save()
