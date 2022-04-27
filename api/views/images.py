from django_filters.filterset import filterset_factory
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.data.models import PrivateImage
from api.serializers.images import ListImageSerializer
from api.views.shared.mixins import FindPageMixin, ProcessSerializerMixin
from api.views.shared.pagination import SinglePagePagination


class BaseImageViewSet(ListModelMixin, GenericViewSet):

    parser_classes = [JSONParser]

    serializer_class = ListImageSerializer

    def get_queryset(self):
        return PrivateImage.objects.all()


class ImageViewSet(ProcessSerializerMixin, BaseImageViewSet):

    filter_backends = [DjangoFilterBackend]

    filterset_class = filterset_factory(PrivateImage, fields=['id'])

    @action(['post'], detail=False, url_path='delete_one')
    def delete_one(self, request, *args, **kwargs):
        PrivateImage.objects.delete_with_file([request.data.get('id')])
        return Response({})


class CarouselViewSet(FindPageMixin, BaseImageViewSet):

    pagination_class = SinglePagePagination

    @action(['get'], detail=False, url_path='find_page')
    def find_page(self, request, *args, **kwargs):
        page = self.get_page_for_object(request.query_params.get('id'))
        return Response({'page': page})
