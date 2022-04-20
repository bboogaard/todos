from services.export.service import CodeSnippetExportService, FileExportService, ImageExportService, NoteExportService,\
    TodoExportService


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


class FileExportServiceFactory:

    @classmethod
    def create(cls, file_type: str):
        return FileExportService() if file_type == 'file' else ImageExportService()
