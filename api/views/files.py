from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.data.models import PrivateFile
from api.serializers.files import ListFileSerializer
from api.views.shared.mixins import ProcessSerializerMixin


class FileViewSet(ListModelMixin, ProcessSerializerMixin, GenericViewSet):

    parser_classes = [JSONParser]

    serializer_class = ListFileSerializer

    def get_queryset(self):
        return PrivateFile.objects.all()

    @action(['post'], detail=False, url_path='delete_one')
    def delete_one(self, request, *args, **kwargs):
        PrivateFile.objects.delete_with_file([request.data.get('id')])
        return Response({})
