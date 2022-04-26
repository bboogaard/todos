import json

from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.test import APIRequestFactory, force_authenticate

from api.views.events import EventViewSet
from api.views.images import ImageViewSet
from api.views.internal.models import Event, Image


class ViewSetFactory:

    def __init__(self, user):
        self.user = user

    def image_list(self, data=None, **extra):
        request = self._create_get('api/v1/images', data, **extra)
        images = self.call_view(ImageViewSet.as_view({'get': 'list'}), request)
        return list(map(lambda i: Image.from_dict(i), images)) if images is not None else []

    def event_list(self, data=None, **extra):
        request = self._create_get('api/v1/events', data, **extra)
        events = self.call_view(EventViewSet.as_view({'get': 'list'}), request)
        return list(map(lambda e: Event.from_dict(e), events)) if events is not None else []

    def event_detail(self, pk, data=None, **extra):
        request = self._create_get(f'api/v1/images/{pk}', data, **extra)
        event = self.call_view(EventViewSet.as_view({'get': 'retrieve'}), request, pk=pk)
        return Event.from_dict(event) if event is not None else None

    def event_create(self, data=None, **extra):
        request = self._create_post('api/v1/events/create_one', data, **extra)
        event = self.call_view(EventViewSet.as_view({'post': 'create_one'}), request)
        return Event.from_dict(event) if event is not None else None

    def event_update(self, data=None, **extra):
        request = self._create_post('api/v1/events/update_one', data, **extra)
        event = self.call_view(EventViewSet.as_view({'post': 'update_one'}), request)
        return Event.from_dict(event) if event is not None else None

    @staticmethod
    def call_view(view, request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        if str(response.status_code)[0] != '2':
            return None

        response.render()
        try:
            return json.loads(response.content)
        except ValueError:
            return None

    def _create_get(self, path, data, **extra):
        request = APIRequestFactory().get(path + '?format=json', data, **extra)
        force_authenticate(request, self.user)
        return request

    def _create_post(self, path, data, **extra):
        data = json.dumps(data, cls=DjangoJSONEncoder)
        extra['content_type'] = 'application/json'
        request = APIRequestFactory().post(path + '?format=json', data, **extra)
        force_authenticate(request, self.user)
        return request
