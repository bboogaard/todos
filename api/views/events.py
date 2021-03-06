from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.data.models import Event
from api.serializers.events import CreateEventSerializer, DaysSerializer, EventSerializer, NextWeekSerializer, \
    PrevWeekSerializer, UpdateEventSerializer, WeeksSerializer
from api.views.filters import EventFilterSet
from api.views.shared.mixins import CreateMixin, ExportMixin
from services.export.factory import ExportServiceFactory


class EventViewSet(ListModelMixin, RetrieveModelMixin, CreateMixin, ExportMixin, GenericViewSet):

    filter_backends = [DjangoFilterBackend]

    filterset_class = EventFilterSet

    parser_classes = [JSONParser]

    serializer_class = EventSerializer

    @property
    def service(self):
        return ExportServiceFactory.events()

    def get_queryset(self):
        return Event.objects.all()

    @action(['post'], detail=False, url_path='create_one')
    def create_one(self, request, *args, **kwargs):
        return self.create_with_response(CreateEventSerializer, request, EventSerializer)

    @action(['post'], detail=False, url_path='update_one')
    def update_one(self, request, *args, **kwargs):
        return self.create_with_response(UpdateEventSerializer, request, EventSerializer)

    @action(['post'], detail=False, url_path='delete_one')
    def delete_one(self, request, *args, **kwargs):
        Event.objects.filter(pk=request.data.get('id')).delete()
        return Response({})

    @action(['get'], detail=False, url_path='days')
    def days(self, request, *args, **kwargs):
        return self.validate_with_response(DaysSerializer, request, data=request.query_params)

    @action(['get'], detail=False, url_path='slots')
    def slots(self, request, *args, **kwargs):
        return Response({
            'slots': settings.CALENDAR_SLOTS
        })

    @action(['get'], detail=False, url_path='weeks')
    def weeks(self, request, *args, **kwargs):
        return self.validate_with_response(WeeksSerializer, request, data=request.query_params)

    @action(['get'], detail=False, url_path='weeks/prev')
    def prev_week(self, request, *args, **kwargs):
        return self.validate_with_response(PrevWeekSerializer, request, data=request.query_params)

    @action(['get'], detail=False, url_path='weeks/next')
    def next_week(self, request, *args, **kwargs):
        return self.validate_with_response(NextWeekSerializer, request, data=request.query_params)
