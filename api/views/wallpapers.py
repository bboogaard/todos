from django_filters.filterset import filterset_factory
from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.data.models import Gallery, Wallpaper
from api.serializers.wallpapers import CreateWallpaperSerializer, ListWallpaperSerializer, UpdateWallpaperSerializer
from api.views.shared.mixins import ProcessSerializerMixin
from api.views.shared.pagination import SinglePagePagination


class BaseWallpaperViewSet(ListModelMixin, GenericViewSet):

    serializer_class = ListWallpaperSerializer

    def get_queryset(self):
        return Wallpaper.objects.order_by('gallery', 'position')


class WallpaperViewSet(ProcessSerializerMixin, BaseWallpaperViewSet):

    @action(['get'], detail=False, url_path='wallpaper-list', renderer_classes=[TemplateHTMLRenderer])
    def wallpaper_list(self, request, *args, **kwargs):
        return Response({
            'galleries': Gallery.objects.all(),
            'wallpaper_vars': {
                'urls': {
                    'create': reverse('api:wallpapers-create-one'),
                    'update': reverse('api:wallpapers-update-one'),
                    'delete': reverse('api:wallpapers-delete-many'),
                    'list': reverse('api:wallpapers-list')
                }
            }
        }, template_name='wallpapers/wallpaper_list.html')

    @action(['post'], detail=False, url_path='create_one', parser_classes=[FormParser, MultiPartParser])
    def create_one(self, request, *args, **kwargs):
        self.process_serializer(CreateWallpaperSerializer, request)
        return Response({})

    @action(['post'], detail=False, url_path='update_one')
    def update_one(self, request, *args, **kwargs):
        self.process_serializer(UpdateWallpaperSerializer, request)
        return Response({})

    @action(['post'], detail=False, url_path='delete_many')
    def delete_many(self, request, *args, **kwargs):
        ids = request.data.get('id')
        Wallpaper.objects.filter(pk__in=ids).delete()
        return Response({})


class BackgroundViewSet(BaseWallpaperViewSet):

    filter_backends = [DjangoFilterBackend]

    filterset_class = filterset_factory(Wallpaper, fields=['gallery'])

    pagination_class = SinglePagePagination
