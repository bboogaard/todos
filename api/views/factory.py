import json

from rest_framework.test import APIRequestFactory, force_authenticate

from api.views.images import ImageViewSet
from api.views.utils import convert_dict


class ViewSetFactory:

    def __init__(self, user):
        self.user = user

    def image_list(self, data=None, **extra):
        request = APIRequestFactory().get('api/v1/images?format=json', data, **extra)
        force_authenticate(request, self.user)
        images = self.call_view(ImageViewSet.as_view({'get': 'list'}), request)
        return list(map(convert_dict, images)) if images is not None else []

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
