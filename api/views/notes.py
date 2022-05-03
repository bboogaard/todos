from django_filters.filterset import filterset_factory
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.data.models import Note
from api.serializers.notes import CreateNoteSerializer, ListNoteSerializer, UpdateNoteSerializer
from api.views.shared.mixins import ExportMixin
from api.views.shared.pagination import SinglePagePagination
from services.export.factory import ExportServiceFactory


class NoteViewSet(ListModelMixin, ExportMixin, GenericViewSet):

    filter_backends = [DjangoFilterBackend]

    filterset_class = filterset_factory(Note, fields=['id'])

    pagination_class = SinglePagePagination

    parser_classes = [JSONParser]

    serializer_class = ListNoteSerializer

    @property
    def service(self):
        return ExportServiceFactory.notes()

    def get_queryset(self):
        return Note.objects.active()

    @action(['post'], detail=False, url_path='create_one')
    def create_one(self, request, *args, **kwargs):
        self.process_serializer(CreateNoteSerializer, request)
        return Response({})

    @action(['post'], detail=False, url_path='update_one')
    def update_one(self, request, *args, **kwargs):
        self.process_serializer(UpdateNoteSerializer, request)
        return Response({})

    @action(['post'], detail=False, url_path='delete_one')
    def delete_one(self, request, *args, **kwargs):
        Note.objects.deactivate([request.data.get('id')])
        return Response({})
