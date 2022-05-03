from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.data.models import CodeSnippet
from api.serializers.snippets import CreateCodeSnippetSerializer, ListCodeSnippetSerializer, UpdateCodeSnippetSerializer
from api.views.shared.mixins import ExportMixin
from api.views.shared.pagination import SinglePagePagination
from services.export.factory import ExportServiceFactory


class CodeSnippetViewSet(ListModelMixin, ExportMixin, GenericViewSet):

    pagination_class = SinglePagePagination

    parser_classes = [JSONParser]

    serializer_class = ListCodeSnippetSerializer

    @property
    def service(self):
        return ExportServiceFactory.snippets()

    def get_queryset(self):
        return CodeSnippet.objects.all()

    @action(['post'], detail=False, url_path='create_one')
    def create_one(self, request, *args, **kwargs):
        self.process_serializer(CreateCodeSnippetSerializer, request)
        return Response({})

    @action(['post'], detail=False, url_path='update_one')
    def update_one(self, request, *args, **kwargs):
        self.process_serializer(UpdateCodeSnippetSerializer, request)
        return Response({})

    @action(['post'], detail=False, url_path='delete_one')
    def delete_one(self, request, *args, **kwargs):
        CodeSnippet.objects.filter(pk=request.data.get('id')).delete()
        return Response({})
