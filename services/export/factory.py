from services.export.service import NoteExportService, TodoExportService


class ExportServiceFactory:

    @classmethod
    def todos(cls):
        return TodoExportService()

    @classmethod
    def notes(cls):
        return NoteExportService()
