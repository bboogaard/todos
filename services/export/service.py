from services.export.api import ExportApi

from api.data import models as data_models
from services.export.models import CodeSnippet, Note, Todo


class TodoExportService(ExportApi):

    item_class = Todo

    model_class = data_models.Todo

    def get_queryset(self):
        return self.model_class.objects.active()


class NoteExportService(ExportApi):

    item_class = Note

    model_class = data_models.Note

    def get_queryset(self):
        return self.model_class.objects.active()


class CodeSnippetExportService(ExportApi):

    item_class = CodeSnippet

    model_class = data_models.CodeSnippet

    def get_queryset(self):
        return self.model_class.objects.all()
