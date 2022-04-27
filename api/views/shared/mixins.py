from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from lib.utils import chunks


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


class FindPageMixin(GenericViewSet):

    def get_page_for_object(self, pk):
        id_list = self.filter_queryset(self.get_queryset()).only('id').values_list('id', flat=True)
        pages = list(enumerate(list(chunks(id_list, self.paginator.page_size)), 1))
        try:
            return next(filter(lambda p: int(pk) in p[1], pages), None)[0]
        except (TypeError, ValueError):
            return 1
