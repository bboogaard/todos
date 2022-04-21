from django_filters.filterset import filterset_factory
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.data.models import PrivateImage
from api.serializers.images import ListImageSerializer
from api.views.shared.mixins import ProcessSerializerMixin


class ImageViewSet(ListModelMixin, ProcessSerializerMixin, GenericViewSet):

    filter_backends = [DjangoFilterBackend]

    filterset_class = filterset_factory(PrivateImage, fields=['id'])

    parser_classes = [JSONParser]

    serializer_class = ListImageSerializer

    def get_queryset(self):
        return PrivateImage.objects.all()

    @action(['post'], detail=False, url_path='delete_one')
    def delete_one(self, request, *args, **kwargs):
        PrivateImage.objects.delete_with_file([request.data.get('id')])
        return Response({})
