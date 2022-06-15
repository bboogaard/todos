from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.data.models import Gallery
from api.serializers.galleries import UpdateGallerySerializer
from api.views.shared.mixins import ProcessSerializerMixin


class GalleryViewSet(ProcessSerializerMixin, GenericViewSet):

    @action(['post'], detail=False, url_path='update_many')
    def update_many(self, request, *args, **kwargs):
        galleries = self.process_serializer(UpdateGallerySerializer, request, many=True)
        Gallery.objects.filter(pk__in=[gallery.pk for gallery in galleries]).update(active=False)
        Gallery.objects.bulk_update(galleries, fields=['active'])
        return Response({})
