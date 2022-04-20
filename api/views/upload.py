from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.serializers.upload import UploadSerializer
from api.views.shared.mixins import ProcessSerializerMixin


class UploadViewSet(ProcessSerializerMixin, GenericViewSet):

    parser_classes = [FormParser, MultiPartParser]

    @action(['post'], detail=False, url_path='upload_one')
    def upload_one(self, request, *args, **kwargs):
        self.process_serializer(UploadSerializer, request)
        return Response({})
