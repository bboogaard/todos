from services.export.service import CodeSnippetExportService, NoteExportService, TodoExportService


class ExportServiceFactory:

    @classmethod
    def todos(cls):
        return TodoExportService()

    @classmethod
    def notes(cls):
        return NoteExportService()

    @classmethod
    def snippets(cls):
        return CodeSnippetExportService()
