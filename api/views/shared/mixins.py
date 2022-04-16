from rest_framework.viewsets import GenericViewSet


class ProcessSerializerMixin(GenericViewSet):

    def process_serializer(self, serializer_class, request, **kwargs):
        self.serializer_class = serializer_class
        serializer = self.get_serializer(data=request.data, **kwargs)
        serializer.is_valid(raise_exception=True)
        return serializer.save()
