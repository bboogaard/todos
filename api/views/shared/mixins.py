from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class ProcessSerializerMixin(GenericViewSet):

    def process_serializer(self, serializer_class, request, **kwargs):
        self.serializer_class = serializer_class
        serializer = self.get_serializer(data=request.data, **kwargs)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def validate_serializer(self, serializer_class, request, **kwargs):
        self.serializer_class = serializer_class
        serializer = self.get_serializer(data=request.query_params, **kwargs)
        serializer.is_valid(raise_exception=True)
        return serializer.data


class CreateMixin(ProcessSerializerMixin):

    def create_with_response(self, serializer_class, request, response_serializer_class, **kwargs):
        instance = self.process_serializer(serializer_class, request, **kwargs)
        response_serializer = response_serializer_class(instance=instance)
        return Response(response_serializer.data)

    def validate_with_response(self, serializer_class, request, **kwargs):
        data = self.validate_serializer(serializer_class, request, **kwargs)
        return Response(data)
