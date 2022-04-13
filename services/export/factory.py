from services.export.service import TodoExportService


class ExportServiceFactory:

    @classmethod
    def todos(cls):
        return TodoExportService()
