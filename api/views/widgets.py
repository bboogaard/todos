from django.template.context import RequestContext
from django.urls import reverse
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.data.models import Widget
from api.serializers.widgets import ListWidgetSerializer, UpdateWidgetSerializer
from api.views.shared.mixins import ProcessSerializerMixin
from widgets.service.factory import WidgetRendererFactory


class WidgetViewSet(ProcessSerializerMixin, ListModelMixin, GenericViewSet):

    serializer_class = ListWidgetSerializer

    def get_queryset(self):
        return Widget.objects.order_by('position')

    @action(['get'], detail=False, url_path='widget-list', renderer_classes=[TemplateHTMLRenderer])
    def widget_list(self, request, *args, **kwargs):
        return Response({
            'widget_vars': {
                'urls': {
                    'update': reverse('api:widgets-update-many'),
                    'list': reverse('api:widgets-list')
                }
            }
        }, template_name='widgets/widget_list.html')

    @action(['get'], detail=False, url_path=r'(?P<pk>\d+)/render')
    def render(self, request, pk, *args, **kwargs):
        html = WidgetRendererFactory.get_renderer(self.get_object()).render_content(
            RequestContext(request, {'request': request})
        )
        return Response({'html': html})

    @action(['post'], detail=False, url_path='update_many')
    def update_many(self, request, *args, **kwargs):
        self.process_serializer(UpdateWidgetSerializer, request, many=True)
        return Response({})
