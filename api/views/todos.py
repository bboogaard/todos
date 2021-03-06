from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.data.models import Todo
from api.serializers.todos import CreateTodoSerializer, ListTodoSerializer, UpdateTodoSerializer
from api.views.shared.mixins import ExportMixin
from services.export.factory import ExportServiceFactory


class TodoViewSet(ListModelMixin, ExportMixin, GenericViewSet):

    parser_classes = [JSONParser]

    filter_backends = [filters.SearchFilter]

    search_fields = ['description']

    serializer_class = ListTodoSerializer

    @property
    def service(self):
        return ExportServiceFactory.todos()

    def get_queryset(self):
        backend = self.filter_backends[0]()
        queryset = Todo.objects.all()
        return queryset.active() if not backend.get_search_terms(self.request) else queryset.inactive()

    @action(['post'], detail=False, url_path='create_many')
    def create_many(self, request, *args, **kwargs):
        todos = self.process_serializer(CreateTodoSerializer, request, many=True)
        Todo.objects.bulk_create(todos)
        return Response({})

    @action(['post'], detail=False, url_path='update_many')
    def update_many(self, request, *args, **kwargs):
        todos = self.process_serializer(UpdateTodoSerializer, request, many=True)
        Todo.objects.bulk_update(todos, fields=['description'])
        return Response({})

    @action(['post'], detail=False, url_path='delete_many')
    def delete_many(self, request, *args, **kwargs):
        Todo.objects.deactivate(request.data.get('id'))
        return Response({})

    @action(['post'], detail=False, url_path='activate_many')
    def activate_many(self, request, *args, **kwargs):
        Todo.objects.activate(request.data.get('id'))
        return Response({})
