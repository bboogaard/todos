from collections import OrderedDict

from django_filters.filterset import filterset_factory
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.data.models import Note
from api.serializers.notes import CreateNoteSerializer, ListNoteSerializer, UpdateNoteSerializer
from api.views.shared.mixins import ProcessSerializerMixin


class NotesPagination(PageNumberPagination):
    page_size = 1

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('page', self.page.number)
        ]))


class NoteViewSet(ListModelMixin, ProcessSerializerMixin, GenericViewSet):

    filter_backends = [DjangoFilterBackend]

    filterset_class = filterset_factory(Note, fields=['id'])

    pagination_class = NotesPagination

    parser_classes = [JSONParser]

    serializer_class = ListNoteSerializer

    def get_queryset(self):
        return Note.objects.active().order_by('-activate_date')

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
