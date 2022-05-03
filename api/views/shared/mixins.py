from django.http.response import FileResponse
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.serializers.shared.serializers import ExportSerializer, ImportSerializer
from lib.utils import chunks
from services.export.api import ExportApi
from services.export.factory import FileExportServiceFactory


class ProcessSerializerMixin(GenericViewSet):

    def process_serializer(self, serializer_class, request, data=None, **kwargs):
        serializer = self._create_and_validate(serializer_class, request, data=data, **kwargs)
        return serializer.save()

    def validate_serializer(self, serializer_class, request, data=None, **kwargs):
        serializer = self._create_and_validate(serializer_class, request, data=data, **kwargs)
        return serializer.data

    def _create_and_validate(self, serializer_class, request, data=None, **kwargs):
        self.serializer_class = serializer_class
        serializer = self.get_serializer(data=data or request.data, **kwargs)
        serializer.is_valid(raise_exception=True)
        return serializer


class CreateMixin(ProcessSerializerMixin):

    def create_with_response(self, serializer_class, request, response_serializer_class, data=None, **kwargs):
        instance = self.process_serializer(serializer_class, request, data=data, **kwargs)
        response_serializer = response_serializer_class(instance=instance)
        return Response(response_serializer.data)

    def validate_with_response(self, serializer_class, request, data=None, **kwargs):
        data = self.validate_serializer(serializer_class, request, data=data, **kwargs)
        return Response(data)


class FindPageMixin(GenericViewSet):

    def get_page_for_object(self, pk):
        id_list = self.filter_queryset(self.get_queryset()).only('id').values_list('id', flat=True)
        pages = list(enumerate(list(chunks(id_list, self.paginator.page_size)), 1))
        try:
            return next(filter(lambda p: int(pk) in p[1], pages), None)[0]
        except (TypeError, ValueError):
            return 1


class ExportMixin(ProcessSerializerMixin):

    @property
    def service(self) -> ExportApi:
        raise NotImplementedError()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['export_file_extension'] = '.txt'
        return context

    @action(['post'], detail=False, url_path='export', parser_classes=[FormParser, MultiPartParser])
    def export_items(self, request, *args, **kwargs):
        data = self.validate_serializer(ExportSerializer, request)
        fh = self.service.dump()
        return FileResponse(fh, filename=data['filename'], as_attachment=True)

    @action(['post'], detail=False, url_path='import', parser_classes=[FormParser, MultiPartParser])
    def import_items(self, request, *args, **kwargs):
        data = self.validate_serializer(ImportSerializer, request)
        self.service.load(data['file'])
        return Response({})


class FileExportMixin(ProcessSerializerMixin):

    file_export_type: str

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['export_file_extension'] = '.zip'
        return context

    @action(['post'], detail=False, url_path='export', parser_classes=[FormParser, MultiPartParser])
    def export_files(self, request, *args, **kwargs):
        data = self.validate_serializer(ExportSerializer, request)
        fh = FileExportServiceFactory.create(self.file_export_type).dump()
        return FileResponse(fh, filename=data['filename'], as_attachment=True)

    @action(['post'], detail=False, url_path='import', parser_classes=[FormParser, MultiPartParser])
    def import_files(self, request, *args, **kwargs):
        data = self.validate_serializer(ImportSerializer, request)
        FileExportServiceFactory.create(self.file_export_type).load(data['file'])
        return Response({})
